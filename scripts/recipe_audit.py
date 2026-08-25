#!/usr/bin/env python3
"""Mechanised recipe audit for snappyHexMesh grid ladders.

WHY THIS FILE EXISTS
====================
``docs/charters/VERIFICATION_CHARTER.md`` section 3.2 rule 3 reads, verbatim:

    A recipe audit precedes an order.  The B-52's ``recipe_audit`` set the
    standard in this corpus and it is cheap: read the refinement level from each
    rung's own dictionary and refuse a triple that does not share one.

It was written as checkable and left UNMECHANISED, and ``docs/LESSONS.md``
``L-303`` is what that cost.  The ``ahmed_25`` "grid ladder" carries
``observed_order`` **1.95** -- monotone, inside its 0.5-2.5 window, plausible --
and is not a geometrically similar family at all.  Read from the three rungs' own
dictionaries:

    rung        background block   background cells   body level   eMesh
    coarse      (42  9 25)                    9,450   (2 3)            2
    medium      (60 13 36)                   28,080   (2 3)            2
    production  (60 13 36)                   28,080   (3 4)            3

**One triple, two refinement mechanisms.**  Gap 1 scales the background block
x2.9714 with the snappy recipe held fixed -- that is legitimate, and it is what a
ladder should look like.  Gap 2 holds the background byte-identical and changes
the recipe instead.  *That mixture is why the defect survived inspection: the
first gap looks exactly right.*  Four of the five stored guards on that ladder
PASS (``distinct_rungs``, ``monotone``, ``order_window``, ``increment_trend``);
the single failure, ``extrapolation_sanity``, fires for an unrelated reason.
**No guard in the set was looking at the recipe.**  The protection was accidental.

The same defect is section 3.2's own NACA 4412 worked example, rung for rung --
"coarse and medium are both ``level (2 3)`` and differ only in background block
density; production alone is ``level (3 4)``".  NACA was caught only because its
``p`` came out at 10.467 and blew the window.  Ahmed was not caught, because
1.95 looked right.  A guard that only fires when the number looks wrong is not a
guard.

THE RULE THIS FILE ENCODES (L-303, stated so it can be applied without judgement)
=================================================================================
    A 3-D mesh ladder is not admissible as a Roache ladder unless the BACKGROUND
    mesh is scaled between every pair of adjacent rungs and the refinement recipe
    is otherwise held FIXED.

So, per adjacent pair, this file asks two independent questions and reports both:

    did the RECIPE change?        (snappyHexMeshDict: refinementSurfaces levels,
                                   feature eMesh levels, refinementRegions levels,
                                   nCellsBetweenLevels, resolveFeatureAngle,
                                   castellatedMesh/snap/addLayers, and the whole
                                   addLayersControls layer spec)
    did the BACKGROUND change?    (blockMeshDict: scale, vertices, every hex
                                   block's (nx ny nz) and its grading)

and classifies the pair:

    recipe fixed,   background changed  ->  SCALED         legitimate
    recipe fixed,   background fixed    ->  IDENTICAL      the rungs are the same mesh
    recipe changed, background fixed    ->  RECIPE-FORKED  the Ahmed gap-2 defect
    recipe changed, background changed  ->  MIXED          two knobs at once

**The classification is PER GAP, and the ladder verdict is reported beside it,
never instead of it.**  A single ladder-level boolean would have hidden exactly
the Ahmed case, whose first gap is legitimate and whose second is not.

A ``SCALED`` gap is additionally checked for geometric similarity, because
"the background changed" is not the same as "the background was scaled":

    * the vertices must be unchanged        (a moved domain is a different case)
    * the grading must be unchanged         (regraded cells are not scaled cells)
    * every direction must be non-decreasing and the block-cell product must
      strictly increase
    * every direction that carries more than one cell on the coarser rung must
      strictly increase -- L-303 rule 1, "scale all three directions; a
      one-direction bump is not a 3-D refinement".  Counting only the directions
      that already carry cells is what keeps a legitimate 2-D blockMesh
      (nz == 1) from being failed for not refining through its empty direction.

LADDER VERDICT, in the lab's fixed vocabulary (CLAUDE.md rule 1)
================================================================
    PASS          every gap is SCALED and geometrically similar.  This says the
                  ladder is RECIPE-CLEAN.  It says nothing whatever about
                  convergence, and this file never computes an order.
    NOT A RESULT  any gap is RECIPE-FORKED, MIXED, IDENTICAL, or is SCALED but
                  not similar.  Per L-303 that is the label on the LADDER, not a
                  caveat under a value: the triple was never in the CONVERGING
                  branch to begin with.

WHAT THIS FILE REFUSES TO DECIDE (exit 2, never a degraded answer -- CLAUDE.md
rule 4's discipline)
=============================================================================
    * fewer than three rungs
    * a missing ``system/blockMeshDict`` or ``system/snappyHexMeshDict``
    * a dictionary with no parseable ``blocks``/``hex`` entry, or no
      ``castellatedMeshControls``
    * an unresolved ``#include``/``#includeEtc`` inside a scope this audit
      COMPARES (the snappy dict's top level, ``castellatedMeshControls`` or
      ``addLayersControls``; or anywhere in the blockMeshDict).  An include
      inside ``meshQualityControls`` or ``snapControls`` is recorded and does
      not refuse, because no compared field can come from there.

A refusal is not a pass.  Exit codes: **0** audited and PASS, **1** audited and
NOT A RESULT, **2** REFUSED, **3** selftest failure.

NEWLINE NORMALISATION IS LOAD-BEARING
=====================================
Two of these dictionaries differ by md5 ONLY because one copy is CRLF; after
newline normalisation they are byte-identical, vertices included.  An audit that
reports a spurious difference will be ignored, which is worse than not running.
So every comparison here is made on parsed, whitespace-collapsed structure, and
the newline-normalised whole-file sha256 is reported ALONGSIDE it as
corroboration of L-303's byte-identity claim -- never as the comparison itself.
Comments and indentation are likewise invisible to the comparison, and
``--selftest`` carries the false-positive controls that prove it.

THIS FILE TAKES EXPLICIT PATHS AND WALKS THE DISK
=================================================
The ``ahmed_25`` rungs live in ``/home/ubuntu/certonomous-runs/``, OUTSIDE the
git repository, and ``grep -r`` in this environment honours ignore files, so
gitignored and external trees are INVISIBLE to a grep sweep.  ``--discover``
walks the filesystem with ``os.walk``; nothing here consults git or grep.

WHAT THIS FILE CANNOT SEE, stated because a check that overstates its reach is
worse than none
==============================================================================
    * the solver setup: schemes, models, relaxation, iteration counts.  Two rungs
      can share a mesh recipe and still not be one experiment.
    * whether the STL geometry each rung snapped to is the same file.  The
      surface name and its levels are compared; the triangulation is not.
    * anything about the values.  This file never reads a coefficient, never
      fits an order, and never re-grades a stored verdict.  It decides
      admissibility, which is upstream of grading and cannot substitute for it.
    * whether a PASS ladder converged.  ``PASS`` here means RECIPE-CLEAN only.

USAGE
=====
    python3 scripts/recipe_audit.py CASE1 CASE2 CASE3 [CASE4 ...]
    python3 scripts/recipe_audit.py --certificate CASE [CASE ...]
    python3 scripts/recipe_audit.py --discover ROOT [ROOT ...]
    python3 scripts/recipe_audit.py --selftest
    (add --json to any of the first three for machine-readable output)

Rungs are audited in the order given.  ``--certificate`` prints the per-rung mesh
birth certificate D514 names as the compliance artifact and emits no verdict.
``--discover`` enumerates candidate cases and emits no verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

# ---------------------------------------------------------------------------
# Gap classes and ladder verdicts.  The ladder verdicts are CLAUDE.md rule 1's
# fixed vocabulary; the gap classes are structural labels, deliberately NOT
# verdict words, so that no reader mistakes a gap class for a graded outcome.
# ---------------------------------------------------------------------------
SCALED = "SCALED"
IDENTICAL = "IDENTICAL"
RECIPE_FORKED = "RECIPE-FORKED"
MIXED = "MIXED"

VERDICT_PASS = "PASS"
VERDICT_NOT_A_RESULT = "NOT A RESULT"

EXIT_PASS = 0
EXIT_NOT_A_RESULT = 1
EXIT_REFUSED = 2
EXIT_SELFTEST_FAILED = 3

# Scopes of the snappy dict whose contents feed a compared field.  An
# unresolved include in one of these is a refusal; elsewhere it is a note.
COMPARED_SNAPPY_SCOPES = ("<top level>", "castellatedMeshControls", "addLayersControls")


class Refusal(Exception):
    """Raised instead of returning a degraded answer.  Always exit 2."""


def refuse(msg: str) -> "Refusal":
    return Refusal(msg)


# ===========================================================================
# Text normalisation
# ===========================================================================

def normalise_newlines(text: str) -> str:
    """CRLF and lone CR both become LF.  Nothing else is touched.

    This is the ONLY transform applied before the whole-file sha256, so that
    sha reproduces L-303's "byte-identical after newline normalisation" claim
    exactly and nothing more.
    """
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_dict(path: str) -> str:
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        raise refuse(f"cannot read {path}: {exc}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    return normalise_newlines(text)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def collapse_ws(text: str) -> str:
    """Collapse every run of whitespace to one space and strip.

    Indentation and line breaks are formatting, not content.  A comparison that
    can be tripped by re-indentation reports differences nobody caused.
    """
    return re.sub(r"\s+", " ", text).strip()


def strip_comments(text: str) -> str:
    """Remove ``//`` line comments and ``/* */`` block comments, keeping strings.

    OpenFOAM file banners are block comments and the ``// * * * //`` rules are
    line comments; both must be invisible to the comparison, or two dictionaries
    that differ only in their generated header would read as a recipe change.
    """
    out = []
    i, n = 0, len(text)
    in_string = False
    while i < n:
        c = text[i]
        if in_string:
            out.append(c)
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


# ===========================================================================
# A small OpenFOAM-subset parser.
#
# Deliberately not a general one.  It reads the handful of shapes these
# dictionaries actually use -- `key value;`, `key ( ... );`, `key { ... }`, and
# a `#directive` line -- and it reports what it could not read rather than
# guessing.
# ===========================================================================

def _read_group(text: str, i: int, opener: str, closer: str):
    """Read a balanced group starting at ``text[i] == opener``.

    Returns ``(inner_text, index_just_after_closer)``.
    """
    assert text[i] == opener
    depth = 0
    j = i
    n = len(text)
    while j < n:
        if text[j] == opener:
            depth += 1
        elif text[j] == closer:
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    raise refuse(f"unbalanced {opener}{closer} group")


def entries(body: str):
    """Yield ``(key, kind, value)`` for the top-level entries of ``body``.

    ``kind`` is one of ``dict`` / ``list`` / ``scalar`` / ``directive``.
    Quoted keys (``"(lowerWall|motorBike).*"``) are kept verbatim, including
    their quotes, because in a layers spec the pattern IS the key.
    """
    out = []
    i, n = 0, len(body)
    while i < n:
        while i < n and body[i].isspace():
            i += 1
        if i >= n:
            break
        if body[i] == ";":
            i += 1
            continue
        if body[i] == "#":
            j = i
            while j < n and body[j] != "\n":
                j += 1
            out.append((body[i:j].strip(), "directive", ""))
            i = j
            continue
        if body[i] == "}" or body[i] == ")":
            # Stray closer: the caller handed us an unbalanced body.
            raise refuse("unbalanced dictionary body")
        if body[i] == '"':
            end = body.find('"', i + 1)
            if end < 0:
                raise refuse("unterminated quoted key")
            key = body[i:end + 1]
            i = end + 1
        else:
            j = i
            while j < n and (not body[j].isspace()) and body[j] not in "{}();":
                j += 1
            key = body[i:j]
            i = j
        while i < n and body[i].isspace():
            i += 1
        if i >= n:
            break
        if body[i] == "{":
            inner, i = _read_group(body, i, "{", "}")
            out.append((key, "dict", inner))
        elif body[i] == "(":
            inner, i = _read_group(body, i, "(", ")")
            while i < n and body[i] != ";":
                i += 1
            i += 1
            out.append((key, "list", inner))
        elif body[i] == ";":
            out.append((key, "scalar", ""))
            i += 1
        else:
            j = i
            depth = 0
            while j < n:
                if body[j] in "([":
                    depth += 1
                elif body[j] in ")]":
                    depth -= 1
                elif body[j] == ";" and depth == 0:
                    break
                j += 1
            out.append((key, "scalar", body[i:j].strip()))
            i = j + 1
    return out


def find_entry(ents, key):
    for k, kind, value in ents:
        if k == key:
            return kind, value
    return None, None


def scalar(ents, key, default=None):
    kind, value = find_entry(ents, key)
    if kind is None:
        return default
    return collapse_ws(value)


def directives(ents):
    return [k for k, kind, _ in ents if kind == "directive"]


# ===========================================================================
# blockMeshDict -- the BACKGROUND
# ===========================================================================

_GRADING_WORDS = ("simpleGrading", "edgeGrading")


def parse_blocks(blocks_src: str):
    """Parse the ``blocks ( ... )`` list into one record per ``hex`` entry.

    Shapes handled, all of them present in this corpus::

        hex (0 1 2 3 4 5 6 7) (42 9 25) simpleGrading (1 1 1)
        hex (0 1 2 3 4 5 6 7) zoneName (42 9 25) edgeGrading ( ... )
        hex (0 1 2 3 4 5 6 7) (42 9 25)                     [no grading]
    """
    blocks = []
    i, n = 0, len(blocks_src)
    while True:
        m = re.compile(r"(?<![A-Za-z0-9_])hex\s*(?=\()").search(blocks_src, i)
        if not m:
            break
        i = m.end()
        verts_src, i = _read_group(blocks_src, i, "(", ")")
        # Optional zone name between the vertex list and the cell counts.
        j = i
        while j < n and blocks_src[j].isspace():
            j += 1
        zone = None
        if j < n and blocks_src[j] != "(":
            k = j
            while k < n and (not blocks_src[k].isspace()) and blocks_src[k] != "(":
                k += 1
            zone = blocks_src[j:k]
            j = k
            while j < n and blocks_src[j].isspace():
                j += 1
        if j >= n or blocks_src[j] != "(":
            raise refuse("a hex entry has no (nx ny nz) cell-count group")
        counts_src, i = _read_group(blocks_src, j, "(", ")")
        counts = counts_src.split()
        if len(counts) != 3 or not all(c.lstrip("+").isdigit() for c in counts):
            raise refuse(f"a hex entry's cell counts are not three integers: {counts_src.strip()!r}")
        cells = [int(c) for c in counts]
        # Optional grading.
        j = i
        while j < n and blocks_src[j].isspace():
            j += 1
        grading_type, grading = None, None
        for word in _GRADING_WORDS:
            if blocks_src.startswith(word, j):
                grading_type = word
                j += len(word)
                while j < n and blocks_src[j].isspace():
                    j += 1
                if j < n and blocks_src[j] == "(":
                    grading_src, i = _read_group(blocks_src, j, "(", ")")
                    grading = collapse_ws(grading_src)
                break
        blocks.append({
            "vertices": collapse_ws(verts_src),
            "zone": zone,
            "cells": cells,
            "product": cells[0] * cells[1] * cells[2],
            "grading_type": grading_type,
            "grading": grading,
        })
    if not blocks:
        raise refuse("blockMeshDict has no parseable hex block")
    return blocks


def parse_background(path: str):
    """Extract everything this audit treats as THE BACKGROUND."""
    text = read_dict(path)
    body = strip_comments(text)
    ents = entries(body)
    found = directives(ents)
    if found:
        raise refuse(f"blockMeshDict carries an unresolved directive {found[0]!r}; "
                     "this audit will not guess what it expands to")
    kind, blocks_src = find_entry(ents, "blocks")
    if kind != "list":
        raise refuse("blockMeshDict has no `blocks ( ... );` list")
    kind, verts_src = find_entry(ents, "vertices")
    if kind != "list":
        raise refuse("blockMeshDict has no `vertices ( ... );` list")
    verts = collapse_ws(verts_src)
    blocks = parse_blocks(blocks_src)
    scale_value = scalar(ents, "scale")
    if scale_value is None:
        scale_value = scalar(ents, "convertToMeters")
    background = {
        "scale": scale_value,
        "vertices": verts,
        "vertices_sha256": sha256_text(verts),
        "n_vertices": verts.count("("),
        "blocks": blocks,
        "background_cells": sum(b["product"] for b in blocks),
        "n_blocks": len(blocks),
    }
    background["fingerprint"] = fingerprint({
        "scale": background["scale"],
        "vertices": background["vertices"],
        "blocks": blocks,
    })
    background["file_sha256_lf"] = sha256_text(text)
    return background


# ===========================================================================
# snappyHexMeshDict -- the RECIPE
# ===========================================================================

def parse_recipe(path: str):
    """Extract everything this audit treats as THE RECIPE.

    Everything here is a knob that changes WHERE cells are added rather than how
    many the background starts with.  A change in any of them is a change of
    experiment (L-303): a snappy level refines only near the wetted surface, so
    the far field does not change at all and the three meshes are not a
    geometrically similar family.
    """
    text = read_dict(path)
    body = strip_comments(text)
    ents = entries(body)

    top_directives = directives(ents)
    if top_directives:
        raise refuse(f"snappyHexMeshDict carries a top-level directive {top_directives[0]!r}; "
                     "this audit will not guess what it expands to")

    kind, cmc_src = find_entry(ents, "castellatedMeshControls")
    if kind != "dict":
        raise refuse("snappyHexMeshDict has no `castellatedMeshControls { ... }`")
    cmc = entries(cmc_src)
    cmc_directives = directives(cmc)
    if cmc_directives:
        raise refuse(f"castellatedMeshControls carries an unresolved directive "
                     f"{cmc_directives[0]!r}; a compared field could come from it")

    # --- feature (eMesh) refinement -------------------------------------
    features = []
    kind, features_src = find_entry(cmc, "features")
    if kind == "list":
        i, n = 0, len(features_src)
        while i < n:
            k = features_src.find("{", i)
            if k < 0:
                break
            inner, i = _read_group(features_src, k, "{", "}")
            fe = entries(inner)
            features.append({
                "file": scalar(fe, "file"),
                "level": scalar(fe, "level"),
                "levels": scalar(fe, "levels"),
            })
        features.sort(key=lambda f: (f["file"] or "", f["level"] or "", f["levels"] or ""))

    # --- surface refinement ---------------------------------------------
    surfaces = {}
    kind, rs_src = find_entry(cmc, "refinementSurfaces")
    if kind == "dict":
        for key, ekind, value in entries(rs_src):
            if ekind == "dict":
                surfaces[key] = collapse_ws(value)
            elif ekind == "directive":
                raise refuse("refinementSurfaces carries an unresolved directive")

    # --- volume-region refinement ---------------------------------------
    regions = {}
    kind, rr_src = find_entry(cmc, "refinementRegions")
    if kind == "dict":
        for key, ekind, value in entries(rr_src):
            if ekind == "dict":
                regions[key] = collapse_ws(value)
            elif ekind == "directive":
                raise refuse("refinementRegions carries an unresolved directive")

    # --- layers -----------------------------------------------------------
    kind, alc_src = find_entry(ents, "addLayersControls")
    if kind == "dict":
        alc = entries(alc_src)
        alc_directives = directives(alc)
        if alc_directives:
            raise refuse(f"addLayersControls carries an unresolved directive "
                         f"{alc_directives[0]!r}; a compared field could come from it")
        layers_kind, layers_src = find_entry(alc, "layers")
        layer_spec = collapse_ws(layers_src) if layers_kind == "dict" else None
        layer_controls = {k: collapse_ws(v) for k, kd, v in alc if kd != "directive" and k != "layers"}
    else:
        layer_spec = None
        layer_controls = None

    # Includes elsewhere (meshQualityControls, snapControls) are recorded but
    # never refuse: no compared field can come from those scopes.
    uncompared_directives = []
    for key, ekind, value in ents:
        if ekind == "dict" and key not in ("castellatedMeshControls", "addLayersControls"):
            for d in directives(entries(value)):
                uncompared_directives.append(f"{key}:{d}")

    recipe = {
        "castellatedMesh": scalar(ents, "castellatedMesh"),
        "snap": scalar(ents, "snap"),
        "addLayers": scalar(ents, "addLayers"),
        "nCellsBetweenLevels": scalar(cmc, "nCellsBetweenLevels"),
        "resolveFeatureAngle": scalar(cmc, "resolveFeatureAngle"),
        "features": features,
        "refinementSurfaces": surfaces,
        "refinementRegions": regions,
        "layers": layer_spec,
        "addLayersControls": layer_controls,
    }
    recipe["fingerprint"] = fingerprint(recipe)
    recipe["file_sha256_lf"] = sha256_text(text)
    recipe["uncompared_directives"] = sorted(uncompared_directives)
    return recipe


def fingerprint(obj) -> str:
    """A stable sha256 over canonical JSON.  Key order never matters."""
    return sha256_text(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str))


# ===========================================================================
# Per-rung mesh birth certificate (D514's named compliance artifact)
# ===========================================================================

_NCELLS_RE = re.compile(r"nCells\s*:\s*(\d+)")


def read_ncells(case: str):
    """nCells from the rung's OWN ``constant/polyMesh/owner`` note, or None.

    Returned as evidence in the certificate.  It is never used to classify a
    gap: a cell count cannot tell you which knob moved, which is the whole
    reason this file reads dictionaries instead.
    """
    path = os.path.join(case, "constant", "polyMesh", "owner")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "rb") as fh:
            head = fh.read(4096).decode("latin-1")
    except OSError:
        return None
    m = _NCELLS_RE.search(head)
    return int(m.group(1)) if m else None


def read_dim(case: str):
    """dim from the rung's own ``constant/polyMesh/boundary``: 2 if any patch is
    ``empty``, else 3.  ``None`` when the file is absent.

    Reported in the certificate because section 3.1 rule 2 requires a stored
    study to carry the dimensionality its band was fitted with, established from
    the mesh rather than assumed.
    """
    path = os.path.join(case, "constant", "polyMesh", "boundary")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "rb") as fh:
            text = fh.read().decode("latin-1")
    except OSError:
        return None
    return 2 if re.search(r"type\s+empty\s*;", text) else 3


def certificate(case: str):
    """Read one rung.  Raises Refusal rather than returning a partial answer."""
    if not os.path.isdir(case):
        raise refuse(f"case directory does not exist: {case}")
    bmd = os.path.join(case, "system", "blockMeshDict")
    shmd = os.path.join(case, "system", "snappyHexMeshDict")
    if not os.path.isfile(bmd):
        raise refuse(f"no system/blockMeshDict under {case}")
    if not os.path.isfile(shmd):
        raise refuse(f"no system/snappyHexMeshDict under {case}")
    background = parse_background(bmd)
    recipe = parse_recipe(shmd)
    return {
        "case": os.path.abspath(case),
        "background": background,
        "recipe": recipe,
        "n_cells": read_ncells(case),
        "dim": read_dim(case),
    }


# ===========================================================================
# Comparison
# ===========================================================================

def recipe_differences(a, b):
    """List the recipe keys that differ, as ``(key, coarse_value, fine_value)``."""
    diffs = []
    for key in ("castellatedMesh", "snap", "addLayers", "nCellsBetweenLevels",
                "resolveFeatureAngle", "layers"):
        if a[key] != b[key]:
            diffs.append((key, a[key], b[key]))
    if a["features"] != b["features"]:
        diffs.append(("features", a["features"], b["features"]))
    for name in sorted(set(a["refinementSurfaces"]) | set(b["refinementSurfaces"])):
        va, vb = a["refinementSurfaces"].get(name), b["refinementSurfaces"].get(name)
        if va != vb:
            diffs.append((f"refinementSurfaces.{name}", va, vb))
    for name in sorted(set(a["refinementRegions"]) | set(b["refinementRegions"])):
        va, vb = a["refinementRegions"].get(name), b["refinementRegions"].get(name)
        if va != vb:
            diffs.append((f"refinementRegions.{name}", va, vb))
    ca = a["addLayersControls"] or {}
    cb = b["addLayersControls"] or {}
    for name in sorted(set(ca) | set(cb)):
        if ca.get(name) != cb.get(name):
            diffs.append((f"addLayersControls.{name}", ca.get(name), cb.get(name)))
    return diffs


def background_differences(a, b):
    diffs = []
    if a["scale"] != b["scale"]:
        diffs.append(("scale", a["scale"], b["scale"]))
    if a["vertices_sha256"] != b["vertices_sha256"]:
        diffs.append(("vertices", a["vertices_sha256"][:12], b["vertices_sha256"][:12]))
    if a["n_blocks"] != b["n_blocks"]:
        diffs.append(("n_blocks", a["n_blocks"], b["n_blocks"]))
    else:
        for idx, (ba, bb) in enumerate(zip(a["blocks"], b["blocks"])):
            if ba["cells"] != bb["cells"]:
                diffs.append((f"blocks[{idx}].cells", ba["cells"], bb["cells"]))
            if (ba["grading_type"], ba["grading"]) != (bb["grading_type"], bb["grading"]):
                diffs.append((f"blocks[{idx}].grading",
                              f"{ba['grading_type']} {ba['grading']}",
                              f"{bb['grading_type']} {bb['grading']}"))
    return diffs


def similarity_failures(a, b):
    """Why a SCALED gap is nevertheless not a geometric scaling.  Empty == fine."""
    why = []
    if a["vertices_sha256"] != b["vertices_sha256"]:
        why.append("vertices changed (the domain moved, so the rungs are different cases)")
    if a["scale"] != b["scale"]:
        why.append(f"scale changed ({a['scale']} -> {b['scale']})")
    if a["n_blocks"] != b["n_blocks"]:
        why.append(f"block count changed ({a['n_blocks']} -> {b['n_blocks']})")
        return why
    for idx, (ba, bb) in enumerate(zip(a["blocks"], b["blocks"])):
        if (ba["grading_type"], ba["grading"]) != (bb["grading_type"], bb["grading"]):
            why.append(f"blocks[{idx}] grading changed (regraded cells are not scaled cells)")
        if any(y < x for x, y in zip(ba["cells"], bb["cells"])):
            why.append(f"blocks[{idx}] a direction got COARSER: {ba['cells']} -> {bb['cells']}")
        if bb["product"] <= ba["product"]:
            why.append(f"blocks[{idx}] cell product did not strictly increase: "
                       f"{ba['product']} -> {bb['product']}")
        # L-303 rule 1: scale all three directions.  Only the directions that
        # already carry more than one cell are required to move, so a genuine
        # 2-D blockMesh (nz == 1) is not failed for its empty direction.
        active = [k for k in range(3) if ba["cells"][k] > 1]
        moved = [k for k in active if bb["cells"][k] > ba["cells"][k]]
        if active and len(moved) != len(active):
            why.append(f"blocks[{idx}] only {len(moved)} of {len(active)} populated "
                       f"directions were refined: {ba['cells']} -> {bb['cells']} "
                       "(a one-direction bump is not a 3-D refinement)")
    if a["background_cells"] >= b["background_cells"]:
        why.append(f"total background cells did not increase: "
                   f"{a['background_cells']} -> {b['background_cells']}")
    return why


def classify_gap(lo, hi):
    """Classify one adjacent pair.  ``lo`` is the coarser rung as supplied."""
    r_diffs = recipe_differences(lo["recipe"], hi["recipe"])
    b_diffs = background_differences(lo["background"], hi["background"])
    recipe_changed = bool(r_diffs)
    background_changed = bool(b_diffs)

    if recipe_changed and background_changed:
        klass = MIXED
    elif recipe_changed:
        klass = RECIPE_FORKED
    elif background_changed:
        klass = SCALED
    else:
        klass = IDENTICAL

    sim = similarity_failures(lo["background"], hi["background"]) if klass == SCALED else []
    ratio = None
    lo_bg = lo["background"]["background_cells"]
    hi_bg = hi["background"]["background_cells"]
    if lo_bg > 0:
        ratio = hi_bg / lo_bg

    return {
        "coarse": lo["case"],
        "fine": hi["case"],
        "class": klass,
        "recipe_changed": recipe_changed,
        "background_changed": background_changed,
        "recipe_differences": [[k, str(x), str(y)] for k, x, y in r_diffs],
        "background_differences": [[k, str(x), str(y)] for k, x, y in b_diffs],
        "background_cells": [lo_bg, hi_bg],
        "background_cell_ratio": ratio,
        "similarity_failures": sim,
        "admissible": klass == SCALED and not sim,
        # Corroboration only.  Never the comparison itself -- see the module
        # docstring on newline normalisation.
        "blockMeshDict_identical_after_newline_normalisation":
            lo["background"]["file_sha256_lf"] == hi["background"]["file_sha256_lf"],
        "snappyHexMeshDict_identical_after_newline_normalisation":
            lo["recipe"]["file_sha256_lf"] == hi["recipe"]["file_sha256_lf"],
    }


def audit_ladder(cases):
    """Audit a ladder of >= 3 rungs, in the order supplied (coarse to fine)."""
    if len(cases) < 3:
        raise refuse(f"a ladder needs at least 3 rungs; {len(cases)} given. "
                     "Two rungs cannot yield an observed order, so there is "
                     "nothing here for a recipe audit to protect.")
    rungs = [certificate(c) for c in cases]
    gaps = [classify_gap(rungs[i], rungs[i + 1]) for i in range(len(rungs) - 1)]

    reasons = []
    for idx, gap in enumerate(gaps, start=1):
        if gap["class"] == RECIPE_FORKED:
            reasons.append(f"gap {idx} is RECIPE-FORKED: the background is unchanged and "
                           f"the recipe moved ({len(gap['recipe_differences'])} field(s))")
        elif gap["class"] == MIXED:
            reasons.append(f"gap {idx} is MIXED: recipe and background both moved")
        elif gap["class"] == IDENTICAL:
            reasons.append(f"gap {idx} is IDENTICAL: the two rungs are the same mesh")
        elif gap["similarity_failures"]:
            reasons.append(f"gap {idx} scaled the background but is not a geometric "
                           f"scaling: {'; '.join(gap['similarity_failures'])}")

    verdict = VERDICT_PASS if not reasons else VERDICT_NOT_A_RESULT
    return {
        "rungs": rungs,
        "gaps": gaps,
        "verdict": verdict,
        "verdict_reasons": reasons,
        "n_rungs": len(rungs),
        "n_gaps": len(gaps),
        "gap_classes": [g["class"] for g in gaps],
    }


# ===========================================================================
# Reporting
# ===========================================================================

def _short(value, width=64):
    text = str(value)
    return text if len(text) <= width else text[:width - 3] + "..."


def print_certificate(cert, out=sys.stdout):
    bg = cert["background"]
    rp = cert["recipe"]
    print(f"  case                 {cert['case']}", file=out)
    print(f"  background blocks    " + "; ".join(
        f"({' '.join(str(c) for c in b['cells'])}) = {b['product']} cells"
        + (f" {b['grading_type']} ({b['grading']})" if b["grading_type"] else "")
        for b in bg["blocks"]), file=out)
    print(f"  background cells     {bg['background_cells']}", file=out)
    print(f"  vertices sha256      {bg['vertices_sha256'][:16]}  ({bg['n_vertices']} vertices)", file=out)
    print(f"  scale                {bg['scale']}", file=out)
    surfaces = "; ".join(f"{k} {{ {_short(v)} }}" for k, v in sorted(rp["refinementSurfaces"].items()))
    regions = "; ".join(f"{k} {{ {_short(v)} }}" for k, v in sorted(rp["refinementRegions"].items()))
    feats = "; ".join(f"{f['file']} level {f['level'] if f['level'] is not None else f['levels']}"
                      for f in rp["features"])
    print(f"  refinementSurfaces   {surfaces or '(none)'}", file=out)
    print(f"  features (eMesh)     {feats or '(none)'}", file=out)
    print(f"  refinementRegions    {regions or '(none)'}", file=out)
    print(f"  nCellsBetweenLevels  {rp['nCellsBetweenLevels']}", file=out)
    print(f"  castellated/snap/layers  {rp['castellatedMesh']} / {rp['snap']} / {rp['addLayers']}", file=out)
    print(f"  layers spec          {_short(rp['layers'])}", file=out)
    print(f"  nCells (polyMesh)    {cert['n_cells'] if cert['n_cells'] is not None else 'NOT ON DISK'}", file=out)
    print(f"  dim (boundary file)  {cert['dim'] if cert['dim'] is not None else 'NOT ON DISK'}", file=out)
    print(f"  recipe fingerprint   {rp['fingerprint'][:16]}", file=out)
    print(f"  background fingerpr. {bg['fingerprint'][:16]}", file=out)
    if rp["uncompared_directives"]:
        print(f"  NOTE unresolved includes outside compared scopes: "
              f"{', '.join(rp['uncompared_directives'])}", file=out)


def print_report(result, out=sys.stdout):
    print("=" * 78, file=out)
    print("RECIPE AUDIT -- VERIFICATION_CHARTER.md section 3.2 rule 3, mechanised (L-303)", file=out)
    print("=" * 78, file=out)
    for idx, cert in enumerate(result["rungs"], start=1):
        print(f"\nRUNG {idx}", file=out)
        print_certificate(cert, out=out)
    print("\n" + "-" * 78, file=out)
    print("PER-GAP CLASSIFICATION", file=out)
    print("-" * 78, file=out)
    for idx, gap in enumerate(result["gaps"], start=1):
        ratio = gap["background_cell_ratio"]
        print(f"\ngap {idx}: {os.path.basename(gap['coarse'])} -> {os.path.basename(gap['fine'])}", file=out)
        print(f"  class                {gap['class']}"
              + ("" if gap["admissible"] else "   [NOT ADMISSIBLE AS A REFINEMENT STEP]"), file=out)
        print(f"  background cells     {gap['background_cells'][0]} -> {gap['background_cells'][1]}"
              + (f"  (x{ratio:.4f})" if ratio else ""), file=out)
        if gap["recipe_differences"]:
            print("  recipe changed in:", file=out)
            for key, lo, hi in gap["recipe_differences"]:
                print(f"      {key}: {_short(lo)}  ->  {_short(hi)}", file=out)
        else:
            print("  recipe             HELD FIXED", file=out)
        if gap["background_differences"]:
            print("  background changed in:", file=out)
            for key, lo, hi in gap["background_differences"]:
                print(f"      {key}: {_short(lo)}  ->  {_short(hi)}", file=out)
        else:
            print("  background         HELD FIXED", file=out)
        for why in gap["similarity_failures"]:
            print(f"  NOT A SCALING: {why}", file=out)
        if gap["snappyHexMeshDict_identical_after_newline_normalisation"]:
            print("  corroboration: the two snappyHexMeshDict files are byte-identical "
                  "after newline normalisation", file=out)
        if gap["blockMeshDict_identical_after_newline_normalisation"]:
            print("  corroboration: the two blockMeshDict files are byte-identical "
                  "after newline normalisation", file=out)
    print("\n" + "-" * 78, file=out)
    print(f"LADDER VERDICT: {result['verdict']}", file=out)
    print("-" * 78, file=out)
    if result["verdict"] == VERDICT_PASS:
        print("  Every gap scales the background with the recipe held fixed.", file=out)
        print("  This says the ladder is RECIPE-CLEAN and nothing more. It is NOT a", file=out)
        print("  statement about convergence: no order is computed here.", file=out)
    else:
        for reason in result["verdict_reasons"]:
            print(f"  - {reason}", file=out)
        print("  Per L-303 the label belongs to the LADDER, not as a caveat under a", file=out)
        print("  value: the triple was never in the CONVERGING branch to begin with.", file=out)
    print("-" * 78, file=out)


# ===========================================================================
# --discover: enumerate candidate cases by walking the disk
# ===========================================================================

def discover(roots, out=sys.stdout, as_json=False):
    """Walk ``roots`` for case directories and print one certificate line each.

    Enumeration only: this emits NO verdict, because a directory listing does
    not know which cases somebody called one ladder.
    """
    found = []
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            if os.path.basename(dirpath) != "system":
                continue
            if "blockMeshDict" not in filenames or "snappyHexMeshDict" not in filenames:
                continue
            case = os.path.dirname(dirpath)
            try:
                cert = certificate(case)
                found.append({"case": case, "certificate": cert, "refused": None})
            except Refusal as exc:
                found.append({"case": case, "certificate": None, "refused": str(exc)})
    found.sort(key=lambda r: r["case"])
    if as_json:
        print(json.dumps([
            {"case": r["case"],
             "refused": r["refused"],
             "n_cells": r["certificate"]["n_cells"] if r["certificate"] else None,
             "dim": r["certificate"]["dim"] if r["certificate"] else None,
             "background_cells": r["certificate"]["background"]["background_cells"] if r["certificate"] else None,
             "blocks": [b["cells"] for b in r["certificate"]["background"]["blocks"]] if r["certificate"] else None,
             "recipe_fingerprint": r["certificate"]["recipe"]["fingerprint"] if r["certificate"] else None,
             "background_fingerprint": r["certificate"]["background"]["fingerprint"] if r["certificate"] else None,
             "refinementSurfaces": r["certificate"]["recipe"]["refinementSurfaces"] if r["certificate"] else None,
             "features": r["certificate"]["recipe"]["features"] if r["certificate"] else None,
             "refinementRegions": r["certificate"]["recipe"]["refinementRegions"] if r["certificate"] else None,
             "addLayers": r["certificate"]["recipe"]["addLayers"] if r["certificate"] else None}
            for r in found], indent=1), file=out)
    else:
        print(f"{'nCells':>9}  {'bgCells':>8}  {'blocks':<16}  {'recipeFP':<12}  case", file=out)
        for r in found:
            if r["refused"]:
                print(f"{'REFUSED':>9}  {'-':>8}  {'-':<16}  {'-':<12}  {r['case']}  ({r['refused']})", file=out)
                continue
            c = r["certificate"]
            blocks = ",".join("x".join(str(x) for x in b["cells"]) for b in c["background"]["blocks"])
            print(f"{c['n_cells'] if c['n_cells'] is not None else '-':>9}  "
                  f"{c['background']['background_cells']:>8}  {_short(blocks, 16):<16}  "
                  f"{c['recipe']['fingerprint'][:12]:<12}  {r['case']}", file=out)
    n_ok = sum(1 for r in found if not r["refused"])
    # The census goes to stderr under --json so that stdout stays parseable.
    summary_stream = sys.stderr if as_json else out
    print(f"\n{len(found)} candidate case director{'y' if len(found) == 1 else 'ies'} found; "
          f"{n_ok} parsed, {len(found) - n_ok} refused.", file=summary_stream)
    return found


# ===========================================================================
# --selftest
#
# N-T8, registered by the heat-transfer team at commit 792acd8f: "every
# comparator's --selftest must carry a VALUE-checking control ... not a check
# that the key exists".  A selftest that only checks a key exists is exactly why
# a sign defect survived five implementations.
#
# This file's answers are structural rather than numeric, so N-T8 is honoured in
# the form that applies here, in two halves that must BOTH hold:
#
#   VALUE CONTROLS      the extracted values are asserted against fixtures whose
#                       block tuples, level tuples, layer spec and counts are
#                       known BY CONSTRUCTION -- exact equality, not presence.
#
#   MUTATION CONTROLS   for each field the rule depends on, one knob is moved in
#                       a fixture that otherwise passes, and the verdict MUST
#                       flip.  A comparator that silently ignored, say, the
#                       eMesh level would pass every value control and fail M2.
#                       Paired with them are FALSE-POSITIVE controls (M11, M12):
#                       a comment-only and a whitespace-only edit must NOT be
#                       reported as a difference.  Together they are the
#                       planted-zero discipline of CLAUDE.md rule 3 applied to a
#                       structural comparator: the "no difference" answer is only
#                       evidence from a reader shown able to see a difference,
#                       and the "difference" answer is only evidence from a
#                       reader shown able to see none.
#
# The live Ahmed regression fixture is the third half: three real case
# directories that must reproduce a legitimate scaling at gap 1 and
# RECIPE-FORKED at gap 2.  If those directories are gone the selftest REFUSES
# (exit 2) rather than passing quietly -- a control whose population vanished
# reports a clean zero, and this lab has been misled that way three times.
# ===========================================================================

AHMED_25_LIVE_RUNGS = [
    "/home/ubuntu/certonomous-runs/study-ahmed_25-coarse-40aacb",
    "/home/ubuntu/certonomous-runs/study-ahmed_25-medium-b37e86",
    "/home/ubuntu/certonomous-runs/act7-ahmed_25-b14562",
]

_BLOCKMESH_TEMPLATE = """\
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

scale 1;

vertices
(
    (-1 -1 -1)
    ( 1 -1 -1)
    ( 1  1 -1)
    (-1  1 -1)
    (-1 -1  1)
    ( 1 -1  1)
    ( 1  1  1)
    (-1  1  1)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) simpleGrading ({grading})
);

edges ();

boundary
(
    farfield
    {{
        type patch;
        faces ((0 3 2 1));
    }}
);

mergePatchPairs ();
"""

_SNAPPY_TEMPLATE = """\
/*--------------------------------*- C++ -*----------------------------------*\\
| a generated banner, which is a block comment and must be invisible here      |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}}

castellatedMesh true;
snap            true;
addLayers       {add_layers};

geometry
{{
    body {{ type triSurfaceMesh; file "body.stl"; }}
}}

castellatedMeshControls
{{
    maxLocalCells   4000000;
    maxGlobalCells  8000000;
    nCellsBetweenLevels {ncbl};

    features
    (
        {{ file "body.eMesh"; level {emesh}; }}
    );

    refinementSurfaces
    {{
        body {{ level ({surf}); }}
    }}

    resolveFeatureAngle 30;

    refinementRegions
    {{
        nearBody
        {{
            mode inside;
            levels ((1e15 {region}));
        }}
    }}

    locationInMesh (0.9 0 0);
}}

snapControls
{{
    nSmoothPatch 3;
}}

addLayersControls
{{
    relativeSizes true;
    layers
    {{
        body {{ nSurfaceLayers {nlayers}; }}
    }}
    expansionRatio 1.0;
    finalLayerThickness 0.3;
}}

meshQualityControls
{{
    #include "meshQualityDict"
}}

mergeTolerance 1e-6;
"""


def _write_case(root, name, *, nx, ny, nz, grading="1 1 1", surf="2 3", emesh=2,
                region=1, ncbl=3, add_layers="false", nlayers=1, crlf=False,
                extra_comment="", extra_indent=False):
    case = os.path.join(root, name)
    os.makedirs(os.path.join(case, "system"), exist_ok=True)
    bmd = _BLOCKMESH_TEMPLATE.format(nx=nx, ny=ny, nz=nz, grading=grading)
    shmd = _SNAPPY_TEMPLATE.format(add_layers=add_layers, ncbl=ncbl, emesh=emesh,
                                   surf=surf, region=region, nlayers=nlayers)
    if extra_comment:
        shmd = shmd.replace("castellatedMesh true;",
                            f"// {extra_comment}\ncastellatedMesh true;")
    if extra_indent:
        shmd = "\n".join("    " + line if line.strip() else line for line in shmd.split("\n"))
        bmd = "\n".join("  " + line if line.strip() else line for line in bmd.split("\n"))
    if crlf:
        bmd = bmd.replace("\n", "\r\n")
        shmd = shmd.replace("\n", "\r\n")
    with open(os.path.join(case, "system", "blockMeshDict"), "w", newline="") as fh:
        fh.write(bmd)
    with open(os.path.join(case, "system", "snappyHexMeshDict"), "w", newline="") as fh:
        fh.write(shmd)
    return case


def _check(label, got, want, failures):
    if got != want:
        failures.append(f"{label}: got {got!r}, want {want!r}")
        return False
    return True


def selftest(out=sys.stdout):
    failures = []
    root = tempfile.mkdtemp(prefix="recipe_audit_selftest_")
    n_value_controls = 0
    n_mutation_controls = 0
    try:
        # -------------------------------------------------------------------
        # (i) VALUE CONTROLS -- a legitimate scaled ladder, values known by
        #     construction.  Exact equality on every extracted field the rule
        #     depends on, so a parser that returned an empty dict cannot pass.
        # -------------------------------------------------------------------
        legit = [
            _write_case(root, "legit_1", nx=10, ny=10, nz=10),
            _write_case(root, "legit_2", nx=14, ny=14, nz=14),
            _write_case(root, "legit_3", nx=20, ny=20, nz=20),
        ]
        res = audit_ladder(legit)
        for label, got, want in [
            ("legit verdict", res["verdict"], VERDICT_PASS),
            ("legit gap classes", res["gap_classes"], [SCALED, SCALED]),
            ("legit rung1 blocks", res["rungs"][0]["background"]["blocks"][0]["cells"], [10, 10, 10]),
            ("legit rung2 blocks", res["rungs"][1]["background"]["blocks"][0]["cells"], [14, 14, 14]),
            ("legit rung3 blocks", res["rungs"][2]["background"]["blocks"][0]["cells"], [20, 20, 20]),
            ("legit rung1 product", res["rungs"][0]["background"]["background_cells"], 1000),
            ("legit rung2 product", res["rungs"][1]["background"]["background_cells"], 2744),
            ("legit rung3 product", res["rungs"][2]["background"]["background_cells"], 8000),
            ("legit rung1 grading", res["rungs"][0]["background"]["blocks"][0]["grading"], "1 1 1"),
            ("legit rung1 grading type", res["rungs"][0]["background"]["blocks"][0]["grading_type"], "simpleGrading"),
            ("legit rung1 n_vertices", res["rungs"][0]["background"]["n_vertices"], 8),
            ("legit rung3 body level", res["rungs"][2]["recipe"]["refinementSurfaces"]["body"], "level (2 3);"),
            ("legit rung3 eMesh level", res["rungs"][2]["recipe"]["features"][0]["level"], "2"),
            ("legit rung3 eMesh file", res["rungs"][2]["recipe"]["features"][0]["file"], '"body.eMesh"'),
            ("legit rung3 region", res["rungs"][2]["recipe"]["refinementRegions"]["nearBody"],
             "mode inside; levels ((1e15 1));"),
            ("legit rung3 nCellsBetweenLevels", res["rungs"][2]["recipe"]["nCellsBetweenLevels"], "3"),
            ("legit rung3 addLayers", res["rungs"][2]["recipe"]["addLayers"], "false"),
            ("legit rung3 layers spec", res["rungs"][2]["recipe"]["layers"], "body { nSurfaceLayers 1; }"),
            ("legit gap1 ratio", round(res["gaps"][0]["background_cell_ratio"], 4), 2.744),
            ("legit rung3 uncompared includes", res["rungs"][2]["recipe"]["uncompared_directives"],
             ['meshQualityControls:#include "meshQualityDict"']),
        ]:
            n_value_controls += 1
            _check(label, got, want, failures)

        # -------------------------------------------------------------------
        # (ii) THE AHMED SHAPE, synthetic -- gap 1 legitimate, gap 2 forked.
        #      This is the exact defect L-303 records, built from scratch so it
        #      is testable on a box that no longer holds the archives.
        # -------------------------------------------------------------------
        forked = [
            _write_case(root, "forked_1", nx=10, ny=10, nz=10, surf="2 3", emesh=2, region=1),
            _write_case(root, "forked_2", nx=14, ny=14, nz=14, surf="2 3", emesh=2, region=1),
            _write_case(root, "forked_3", nx=14, ny=14, nz=14, surf="3 4", emesh=3, region=2),
        ]
        res = audit_ladder(forked)
        for label, got, want in [
            ("forked verdict", res["verdict"], VERDICT_NOT_A_RESULT),
            ("forked gap classes", res["gap_classes"], [SCALED, RECIPE_FORKED]),
            ("forked gap1 admissible", res["gaps"][0]["admissible"], True),
            ("forked gap2 admissible", res["gaps"][1]["admissible"], False),
            ("forked gap2 background held fixed", res["gaps"][1]["background_changed"], False),
            ("forked gap2 blockMeshDict byte-identical",
             res["gaps"][1]["blockMeshDict_identical_after_newline_normalisation"], True),
            ("forked gap2 changed field count", len(res["gaps"][1]["recipe_differences"]), 3),
            ("forked gap2 changed fields",
             sorted(d[0] for d in res["gaps"][1]["recipe_differences"]),
             ["features", "refinementRegions.nearBody", "refinementSurfaces.body"]),
        ]:
            n_value_controls += 1
            _check(label, got, want, failures)

        # -------------------------------------------------------------------
        # (iii) MIXED -- both knobs move at the same gap.
        # -------------------------------------------------------------------
        mixed = [
            _write_case(root, "mixed_1", nx=10, ny=10, nz=10, surf="2 3"),
            _write_case(root, "mixed_2", nx=14, ny=14, nz=14, surf="2 3"),
            _write_case(root, "mixed_3", nx=20, ny=20, nz=20, surf="3 4"),
        ]
        res = audit_ladder(mixed)
        for label, got, want in [
            ("mixed verdict", res["verdict"], VERDICT_NOT_A_RESULT),
            ("mixed gap classes", res["gap_classes"], [SCALED, MIXED]),
        ]:
            n_value_controls += 1
            _check(label, got, want, failures)

        # -------------------------------------------------------------------
        # (iv) IDENTICAL -- three copies of one mesh are not a ladder.
        # -------------------------------------------------------------------
        same = [
            _write_case(root, "same_1", nx=12, ny=12, nz=12),
            _write_case(root, "same_2", nx=12, ny=12, nz=12),
            _write_case(root, "same_3", nx=12, ny=12, nz=12),
        ]
        res = audit_ladder(same)
        for label, got, want in [
            ("identical verdict", res["verdict"], VERDICT_NOT_A_RESULT),
            ("identical gap classes", res["gap_classes"], [IDENTICAL, IDENTICAL]),
        ]:
            n_value_controls += 1
            _check(label, got, want, failures)

        # -------------------------------------------------------------------
        # (v) CRLF vs LF -- must NOT report a difference, and the fixture must
        #     genuinely differ on disk, or the control is vacuous.  This is the
        #     planted control for the false-positive direction: a comparator
        #     that md5'd raw bytes would fail here, and that is precisely the
        #     spurious difference that gets an audit ignored.
        # -------------------------------------------------------------------
        lf_case = _write_case(root, "crlf_lf", nx=16, ny=16, nz=16, crlf=False)
        crlf_case = _write_case(root, "crlf_crlf", nx=16, ny=16, nz=16, crlf=True)
        raw_lf = open(os.path.join(lf_case, "system", "snappyHexMeshDict"), "rb").read()
        raw_crlf = open(os.path.join(crlf_case, "system", "snappyHexMeshDict"), "rb").read()
        n_value_controls += 1
        if raw_lf == raw_crlf:
            failures.append("CRLF control is VACUOUS: the two fixtures are byte-identical on disk, "
                            "so a comparator that reports no difference has not been shown able "
                            "to see one")
        gap = classify_gap(certificate(lf_case), certificate(crlf_case))
        for label, got, want in [
            ("crlf gap class", gap["class"], IDENTICAL),
            ("crlf recipe_changed", gap["recipe_changed"], False),
            ("crlf background_changed", gap["background_changed"], False),
            ("crlf snappy sha equal after normalisation",
             gap["snappyHexMeshDict_identical_after_newline_normalisation"], True),
        ]:
            n_value_controls += 1
            _check(label, got, want, failures)

        # -------------------------------------------------------------------
        # (vi) MUTATION CONTROLS.  Each moves ONE knob in the otherwise-legit
        #      ladder and requires the verdict to flip in the stated way.  A
        #      comparator that ignored the mutated field would pass every value
        #      control above and fail here.
        # -------------------------------------------------------------------
        mutations = [
            # (id, kwargs for the mutated FINEST rung, expected gap-2 class,
            #  expected verdict, a substring that must appear in the reason text)
            ("M1  refinementSurfaces body level (2 3) -> (3 4)",
             dict(surf="3 4"), RECIPE_FORKED, VERDICT_NOT_A_RESULT, "refinementSurfaces.body"),
            ("M2  feature eMesh level 2 -> 3",
             dict(emesh=3), RECIPE_FORKED, VERDICT_NOT_A_RESULT, "features"),
            ("M3  refinementRegions nearBody levels ((1e15 1)) -> ((1e15 2))",
             dict(region=2), RECIPE_FORKED, VERDICT_NOT_A_RESULT, "refinementRegions.nearBody"),
            ("M4  nCellsBetweenLevels 3 -> 4",
             dict(ncbl=4), RECIPE_FORKED, VERDICT_NOT_A_RESULT, "nCellsBetweenLevels"),
            ("M5  addLayers false -> true",
             dict(add_layers="true"), RECIPE_FORKED, VERDICT_NOT_A_RESULT, "addLayers"),
            ("M6  layers nSurfaceLayers 1 -> 3",
             dict(nlayers=3), RECIPE_FORKED, VERDICT_NOT_A_RESULT, "layers"),
        ]
        for label, kwargs, want_class, want_verdict, want_field in mutations:
            n_mutation_controls += 1
            name = "mut_" + re.sub(r"\W+", "_", label.split()[0])
            # The background is held at rung 2's (14 14 14) ON PURPOSE, so the
            # ONLY thing that moved at gap 2 is the mutated recipe knob. That is
            # the Ahmed gap-2 shape: background byte-identical, recipe forked.
            mutant = _write_case(root, name, nx=14, ny=14, nz=14, **kwargs)
            res = audit_ladder([legit[0], legit[1], mutant])
            ok = _check(f"{label} -> gap2 class", res["gap_classes"][1], want_class, failures)
            ok &= _check(f"{label} -> verdict", res["verdict"], want_verdict, failures)
            fields = [d[0] for d in res["gaps"][1]["recipe_differences"]]
            if not any(f.startswith(want_field) for f in fields):
                failures.append(f"{label}: expected a reported difference in {want_field!r}, "
                                f"got {fields!r}")
                ok = False
            # The mutation must NOT disturb gap 1, which shares no rung with it.
            _check(f"{label} -> gap1 undisturbed", res["gap_classes"][0], SCALED, failures)

        # M7: grading changed.  The recipe is untouched, so the class stays
        # SCALED -- and the ladder must still fail, on similarity.  A comparator
        # that only looked at the class would wave this through.
        n_mutation_controls += 1
        m7 = _write_case(root, "mut_M7", nx=20, ny=20, nz=20, grading="2 1 1")
        res = audit_ladder([legit[0], legit[1], m7])
        _check("M7  grading (1 1 1) -> (2 1 1) -> gap2 class", res["gap_classes"][1], SCALED, failures)
        _check("M7  grading -> verdict", res["verdict"], VERDICT_NOT_A_RESULT, failures)
        if not any("grading changed" in w for w in res["gaps"][1]["similarity_failures"]):
            failures.append(f"M7: expected a 'grading changed' similarity failure, got "
                            f"{res['gaps'][1]['similarity_failures']!r}")

        # M8: vertices changed -- the domain moved, so the rungs are different
        # cases even though every refinement knob is identical.
        n_mutation_controls += 1
        m8 = _write_case(root, "mut_M8", nx=20, ny=20, nz=20)
        m8_path = os.path.join(m8, "system", "blockMeshDict")
        moved = open(m8_path).read().replace("( 1  1  1)", "( 2  2  2)")
        open(m8_path, "w").write(moved)
        res = audit_ladder([legit[0], legit[1], m8])
        _check("M8  vertices moved -> verdict", res["verdict"], VERDICT_NOT_A_RESULT, failures)
        if not any("vertices changed" in w for w in res["gaps"][1]["similarity_failures"]):
            failures.append(f"M8: expected a 'vertices changed' similarity failure, got "
                            f"{res['gaps'][1]['similarity_failures']!r}")

        # M9: one-direction bump -- L-303 rule 1, not a 3-D refinement.
        n_mutation_controls += 1
        m9 = _write_case(root, "mut_M9", nx=28, ny=14, nz=14)
        res = audit_ladder([legit[0], legit[1], m9])
        _check("M9  one-direction bump -> gap2 class", res["gap_classes"][1], SCALED, failures)
        _check("M9  one-direction bump -> verdict", res["verdict"], VERDICT_NOT_A_RESULT, failures)
        if not any("populated" in w for w in res["gaps"][1]["similarity_failures"]):
            failures.append(f"M9: expected a one-direction-bump similarity failure, got "
                            f"{res['gaps'][1]['similarity_failures']!r}")

        # M10: the finest rung is COARSER than the one below it.
        n_mutation_controls += 1
        m10 = _write_case(root, "mut_M10", nx=12, ny=12, nz=12)
        res = audit_ladder([legit[0], legit[1], m10])
        _check("M10 finest rung coarser -> verdict", res["verdict"], VERDICT_NOT_A_RESULT, failures)
        if not any("COARSER" in w or "strictly increase" in w
                   for w in res["gaps"][1]["similarity_failures"]):
            failures.append(f"M10: expected a monotonicity similarity failure, got "
                            f"{res['gaps'][1]['similarity_failures']!r}")

        # M11 / M12: FALSE-POSITIVE controls.  A comment-only and a
        # whitespace-only edit must NOT be reported as a difference.  Without
        # these, a comparator that called everything different would pass
        # M1-M10 and be useless.
        n_mutation_controls += 1
        m11 = _write_case(root, "mut_M11", nx=20, ny=20, nz=20,
                          extra_comment="this comment must be invisible to the audit")
        raw_a = open(os.path.join(legit[2], "system", "snappyHexMeshDict"), "rb").read()
        raw_b = open(os.path.join(m11, "system", "snappyHexMeshDict"), "rb").read()
        if raw_a == raw_b:
            failures.append("M11 control is VACUOUS: the comment was not actually inserted")
        res = audit_ladder([legit[0], legit[1], m11])
        _check("M11 comment-only edit -> gap2 class", res["gap_classes"][1], SCALED, failures)
        _check("M11 comment-only edit -> verdict", res["verdict"], VERDICT_PASS, failures)

        n_mutation_controls += 1
        m12 = _write_case(root, "mut_M12", nx=20, ny=20, nz=20, extra_indent=True)
        raw_c = open(os.path.join(m12, "system", "snappyHexMeshDict"), "rb").read()
        if raw_a == raw_c:
            failures.append("M12 control is VACUOUS: the re-indentation did not change the file")
        res = audit_ladder([legit[0], legit[1], m12])
        _check("M12 whitespace-only edit -> gap2 class", res["gap_classes"][1], SCALED, failures)
        _check("M12 whitespace-only edit -> verdict", res["verdict"], VERDICT_PASS, failures)

        # -------------------------------------------------------------------
        # (vii) REFUSALS -- each must raise, never degrade.
        # -------------------------------------------------------------------
        refusal_cases = []

        def expect_refusal(label, fn):
            refusal_cases.append(label)
            try:
                fn()
            except Refusal:
                return
            failures.append(f"{label}: expected a Refusal, got an answer")

        expect_refusal("two rungs", lambda: audit_ladder(legit[:2]))
        expect_refusal("missing case dir",
                       lambda: audit_ladder(legit[:2] + [os.path.join(root, "nonexistent")]))
        no_snappy = _write_case(root, "no_snappy", nx=20, ny=20, nz=20)
        os.remove(os.path.join(no_snappy, "system", "snappyHexMeshDict"))
        expect_refusal("missing snappyHexMeshDict", lambda: audit_ladder(legit[:2] + [no_snappy]))
        no_blocks = _write_case(root, "no_blocks", nx=20, ny=20, nz=20)
        bp = os.path.join(no_blocks, "system", "blockMeshDict")
        open(bp, "w").write(open(bp).read().replace("hex", "hexx"))
        expect_refusal("no parseable hex block", lambda: audit_ladder(legit[:2] + [no_blocks]))
        bad_include = _write_case(root, "bad_include", nx=20, ny=20, nz=20)
        ip = os.path.join(bad_include, "system", "snappyHexMeshDict")
        open(ip, "w").write(open(ip).read().replace("    resolveFeatureAngle 30;",
                                                    '    #include "someRefinementDict"'))
        expect_refusal("include inside castellatedMeshControls",
                       lambda: audit_ladder(legit[:2] + [bad_include]))
        no_cmc = _write_case(root, "no_cmc", nx=20, ny=20, nz=20)
        cp = os.path.join(no_cmc, "system", "snappyHexMeshDict")
        open(cp, "w").write(open(cp).read().replace("castellatedMeshControls", "somethingElse"))
        expect_refusal("no castellatedMeshControls", lambda: audit_ladder(legit[:2] + [no_cmc]))

        # -------------------------------------------------------------------
        # (viii) LIVE REGRESSION FIXTURE -- the real ahmed_25 rungs.
        # -------------------------------------------------------------------
        live_present = all(os.path.isdir(p) for p in AHMED_25_LIVE_RUNGS)
        if not live_present:
            missing = [p for p in AHMED_25_LIVE_RUNGS if not os.path.isdir(p)]
            print("REFUSED: the live ahmed_25 regression fixture is not on this box.", file=out)
            for p in missing:
                print(f"  missing: {p}", file=out)
            print("A control whose population has vanished reports a clean zero. This "
                  "selftest refuses rather than passing without it.", file=out)
            return EXIT_REFUSED
        res = audit_ladder(AHMED_25_LIVE_RUNGS)
        for label, got, want in [
            ("live ahmed_25 verdict", res["verdict"], VERDICT_NOT_A_RESULT),
            ("live ahmed_25 gap classes", res["gap_classes"], [SCALED, RECIPE_FORKED]),
            ("live ahmed_25 gap1 admissible", res["gaps"][0]["admissible"], True),
            ("live ahmed_25 coarse blocks", res["rungs"][0]["background"]["blocks"][0]["cells"], [42, 9, 25]),
            ("live ahmed_25 medium blocks", res["rungs"][1]["background"]["blocks"][0]["cells"], [60, 13, 36]),
            ("live ahmed_25 fine blocks", res["rungs"][2]["background"]["blocks"][0]["cells"], [60, 13, 36]),
            ("live ahmed_25 coarse bg cells", res["rungs"][0]["background"]["background_cells"], 9450),
            ("live ahmed_25 medium bg cells", res["rungs"][1]["background"]["background_cells"], 28080),
            ("live ahmed_25 fine bg cells", res["rungs"][2]["background"]["background_cells"], 28080),
            ("live ahmed_25 gap1 ratio", round(res["gaps"][0]["background_cell_ratio"], 4), 2.9714),
            ("live ahmed_25 coarse body level",
             res["rungs"][0]["recipe"]["refinementSurfaces"]["body"], "level (2 3);"),
            ("live ahmed_25 fine body level",
             res["rungs"][2]["recipe"]["refinementSurfaces"]["body"], "level (3 4);"),
            ("live ahmed_25 gap2 blockMeshDict byte-identical",
             res["gaps"][1]["blockMeshDict_identical_after_newline_normalisation"], True),
            ("live ahmed_25 gap1 snappy byte-identical",
             res["gaps"][0]["snappyHexMeshDict_identical_after_newline_normalisation"], True),
            ("live ahmed_25 nCells", [r["n_cells"] for r in res["rungs"]], [20621, 45753, 79439]),
            ("live ahmed_25 dim", [r["dim"] for r in res["rungs"]], [3, 3, 3]),
        ]:
            n_value_controls += 1
            _check(label, got, want, failures)

        # -------------------------------------------------------------------
        print(f"selftest: {n_value_controls} value controls, "
              f"{n_mutation_controls} mutation controls "
              f"(10 must-flip + 2 false-positive), "
              f"{len(refusal_cases)} refusal controls, "
              f"live ahmed_25 regression fixture PRESENT.", file=out)
        if failures:
            print(f"\nSELFTEST FAILED -- {len(failures)} control(s) disagreed:", file=out)
            for f in failures:
                print(f"  - {f}", file=out)
            return EXIT_SELFTEST_FAILED
        print("SELFTEST PASS", file=out)
        return EXIT_PASS
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ===========================================================================
# CLI
# ===========================================================================

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Mechanised recipe audit for snappyHexMesh grid ladders "
                    "(VERIFICATION_CHARTER.md 3.2 rule 3; L-303).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="exit 0 PASS, 1 NOT A RESULT, 2 REFUSED, 3 selftest failed.")
    parser.add_argument("cases", nargs="*", help="case directories, coarse to fine")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--certificate", action="store_true",
                        help="print the per-rung mesh birth certificate only, no verdict")
    parser.add_argument("--discover", action="store_true",
                        help="treat the arguments as roots to WALK for case directories; "
                             "enumeration only, no verdict")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    if not args.cases:
        parser.error("give at least one path, or --selftest")

    try:
        if args.discover:
            discover(args.cases, as_json=args.json)
            return EXIT_PASS
        if args.certificate:
            certs = [certificate(c) for c in args.cases]
            if args.json:
                print(json.dumps(certs, indent=1, default=str))
            else:
                for idx, cert in enumerate(certs, start=1):
                    print(f"RUNG {idx}")
                    print_certificate(cert)
                    print()
            return EXIT_PASS
        result = audit_ladder(args.cases)
    except Refusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        print("This audit refuses rather than returning a degraded answer "
              "(CLAUDE.md rule 4). A refusal is not a pass.", file=sys.stderr)
        return EXIT_REFUSED

    if args.json:
        print(json.dumps(result, indent=1, default=str))
    else:
        print_report(result)
    return EXIT_PASS if result["verdict"] == VERDICT_PASS else EXIT_NOT_A_RESULT


if __name__ == "__main__":
    sys.exit(main())
