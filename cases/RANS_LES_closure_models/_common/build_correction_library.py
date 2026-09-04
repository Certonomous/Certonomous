#!/usr/bin/env python3
"""Closure-correction library — schema checker and library.json builder.

Contract: docs/closure/correction_library/SCHEMA.md v1.0 (FROZEN 2026-09-04).
Reasoning: docs/closure/correction_library/ARCHITECTURE.md.

What it does
------------
(a) VALIDATE every entry in <library>/entries/*.md against SCHEMA.md v1.0 —
    every required key present, every controlled vocabulary respected, and every
    refusal rule in SCHEMA §4, §5, §6, §7 enforced.
(b) GENERATE <library>/library.json from the validated YAML blocks. The output is
    deterministic (sorted keys, entries sorted by id, no timestamps, no absolute
    paths) so a regeneration is a no-op diff.

It REFUSES rather than degrades or skips. Exit codes:
    0  every entry valid (and, unless --check, library.json written)
    2  REFUSE — one or more violations; library.json is NOT written
    1  usage / IO error

ZERO COMPUTE. This script never launches a solver and never reads a run directory.

LOCATION NOTE. It lives in cases/RANS_LES_closure_models/_common/ because the
scripts/ routing question raised in ARCHITECTURE §1 is open. It is written so it
can be moved without change: the library directory is discovered by walking up
from the script's own location AND from the working directory looking for the
marker docs/closure/correction_library/SCHEMA.md, and can be overridden with
--library-dir or $CORRECTION_LIBRARY_DIR. Nothing here is a relative path into
the repository.

SCHEMA EXTENSION — DECLARED, NOT INFERRED (see report / ARCHITECTURE §2.2)
--------------------------------------------------------------------------
SCHEMA v1.0 §4 refuses `install_class: fvOptions-source` on an entry "whose
`equation_form` modifies the Reynolds-stress / anisotropy tensor", and §7 refuses
bands, post-hoc field corrections and per-case switching. **v1.0 carries no field
in which an entry states any of those four facts.** Deciding them by pattern-
matching the `equation_form` prose would be a checker guessing at physics, and a
checker that gets physics silently wrong is ARCHITECTURE §0 failure (ii) wearing
a green tick. So this builder requires an explicit, author-asserted `structural`
block:

    structural:
      modifies_anisotropy_tensor:   yes|no    # §4 refused pairing
      is_uncertainty_band:          yes|no    # §7.1 — must be no
      is_post_hoc_field_correction: yes|no    # §7.2 — must be no
      is_per_case_switching:        yes|no    # §7.3 — must be no
      planted_zero_verdict:         PASS|FAIL|none   # §4 field-input duty

This is a schema EXTENSION and needs a dated addendum to the frozen SCHEMA.md
(v1.0 -> v1.1) adding the block to §2's table. It is NOT applied here by editing
the frozen file (CLAUDE.md rule 6). Until that addendum lands, this builder is
strictly stricter than SCHEMA v1.0 and says so in its banner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    sys.stderr.write("build_correction_library: PyYAML is required.\n")
    raise SystemExit(1)

SCHEMA_VERSION = "1.0"
BUILDER_EXTENSION = "1.1-draft-structural-block"
MARKER = Path("docs") / "closure" / "correction_library" / "SCHEMA.md"

# --------------------------------------------------------------------------
# Controlled vocabularies — SCHEMA §2, §3, §4, §5, §6
# --------------------------------------------------------------------------
FAMILIES = ("a", "b", "c", "d", "e", "f")

FLOW_CLASSES = (
    "square_duct_secondary_flow",
    "separation_2d",
    "geometry_transfer_fixed_Re",
    "Re_extrapolation",
    "unsteady_rans",
    "complex_3d",
)

VALIDATION_CASE_ROOTS = ("PH_Breuer", "Parm_PH_29", "DUCT", "CBFS", "NASA_2DWMH")

INSTALL_CLASSES = (
    "dictionary-model",
    "dictionary-coefficients",
    "field-input",
    "fvOptions-source",
    "compiled-library",
)

LIBS_ROUTES = ("ensure_libs", "assert_only", "replace_with_assert")
FAILURE_MODES = ("loud", "silent")
BAND_INTERACTIONS = ("acts_on_k_magnitude", "does_not", "unknown")
STATUSES = ("REGISTERED", "IMPLEMENTED", "REPRODUCED", "REFUTED-IN-REPRODUCTION")

# SCHEMA §6: REPRODUCED is the only state licensed as ladder evidence.
LADDER_EVIDENCE_STATUS = "REPRODUCED"

# Required keys, as dotted paths. SCHEMA §2: "every one REQUIRED. Write `none`
# with a reason; never omit a key."
REQUIRED_KEYS = (
    "id",
    "family",
    "flow_class",
    "validation_cases",
    # SCHEMA Addendum 1 item 3 declares this REQUIRED and this artifact did not
    # enforce it until 2026-09-04 -- a frozen clause with no binding check is a
    # DEAD LEVER, the same shape as SKIP_DIRS in the queue runner. It exists so a
    # paper's own guard case (e.g. SST-QCRC's ZPG flat plate) cannot be dropped
    # silently just because this lab holds no on-disk id for it, which would
    # flatter the entry.
    "paper_validation_cases",
    "equation_form",
    "provenance.path",
    "provenance.title_page_verified",
    "provenance.title_page_quote",
    "provenance.equations",
    "claimed_effect",
    "install_class",
    "install_stanza",
    "model_type_name",
    "libs_required",
    "libs_route",
    "libs_route_justification",
    "failure_mode",
    "contraindications",
    "what_it_cannot_see",
    "band_interaction",
    "status",
    "cost_estimate_core_min",
)

# The declared structural block (builder extension, see module docstring).
STRUCTURAL_KEYS = (
    "structural.modifies_anisotropy_tensor",
    "structural.is_uncertainty_band",
    "structural.is_post_hoc_field_correction",
    "structural.is_per_case_switching",
    "structural.planted_zero_verdict",
)

# SCHEMA §6 rule 7: ladder_evidence is COMPUTED, never taken from the entry.
FORBIDDEN_KEYS = ("ladder_evidence", "is_ladder_evidence", "citable_as_evidence")

ID_RE = re.compile(r"^[a-z0-9_]+$")
SUBID_RE = re.compile(r"^[A-Za-z0-9_]+$")

_BARE_NONE_RE = re.compile(
    r"^\s*(none|none\s+known|no(ne)?\s+that\s+we\s+know\s+of|n/?a|unknown|"
    r"not\s+known|tbd|todo|xxx|\?+)\s*[.;!]?\s*$",
    re.IGNORECASE,
)
_LEADING_NONE_RE = re.compile(
    r"^\s*(none\s+known|none)\s*[-—:;,.]*\s*", re.IGNORECASE
)
# A `none known` contraindication must be ARGUED (SCHEMA §2). The argument must be
# an argument, not a shrug: at least this many characters must follow the token.
MIN_CONTRA_ARGUMENT_CHARS = 40

_PLACEHOLDER_RE = re.compile(r"^\s*(tbd|todo|xxx|fixme|\?+|-+)\s*$", re.IGNORECASE)

# equation_form must cite a source equation number AND a page (SCHEMA §2), unless
# it honestly declares itself unverified.
_EQNUM_RE = re.compile(r"(?:\beq(?:uation)?s?\.?\s*)?\(\s*\d+[a-z]?\s*\)", re.IGNORECASE)
_PAGE_RE = re.compile(r"\bp(?:\.|p\.|age)\s*\d+", re.IGNORECASE)
UNVERIFIED_TOKEN = "UNVERIFIED"


class Violation:
    __slots__ = ("entry_id", "rule", "detail")

    def __init__(self, entry_id: str, rule: str, detail: str) -> None:
        self.entry_id = entry_id
        self.rule = rule
        self.detail = detail

    def render(self) -> str:
        return f"REFUSE: {self.entry_id}: {self.rule} — {self.detail}"

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Violation {self.entry_id} {self.rule}>"


# --------------------------------------------------------------------------
# YAML front-matter handling
# --------------------------------------------------------------------------
def split_front_matter(text: str) -> str:
    """Return the YAML block of a SCHEMA §1 entry file.

    SCHEMA §1: the file opens with a fenced YAML block delimited by `---`,
    followed by free prose. The prose is never parsed.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("file does not open with a '---' fenced YAML block (SCHEMA §1)")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i])
    raise ValueError("YAML block is never closed by a second '---' line (SCHEMA §1)")


def normalise_scalars(node):
    """PyYAML follows YAML 1.1: bare `yes`/`no` parse as booleans.

    SCHEMA §2 writes those values as the strings `yes` and `no`, so normalise
    booleans back to those strings rather than silently comparing True == 'yes'.
    """
    if isinstance(node, bool):
        return "yes" if node else "no"
    if isinstance(node, dict):
        return {k: normalise_scalars(v) for k, v in node.items()}
    if isinstance(node, list):
        return [normalise_scalars(v) for v in node]
    return node


class _Missing:
    """Absent-key sentinel. It is a MODULE-LEVEL singleton on purpose: an earlier
    draft used a `_missing=object()` default argument, which binds a DIFFERENT
    object at def time, so `get_path(...) is MISSING` was never true and every
    absent key read as present. The selftest caught it; the singleton prevents it."""

    __slots__ = ()

    def __repr__(self):
        return "<missing>"

    def __bool__(self):
        return False


MISSING = _Missing()


def get_path(entry: dict, dotted: str):
    """Fetch a dotted key, accepting either a nested mapping or a literal
    dotted key (SCHEMA §2 writes `provenance.path` in the table).
    Returns the MISSING singleton when the key is absent."""
    if dotted in entry:
        return entry[dotted]
    cur = entry
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return MISSING
        cur = cur[part]
    return cur


def _present(value) -> bool:
    if value is MISSING or value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, tuple)) and len(value) == 0:
        return False
    return True


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def validate_entry(entry: dict, label: str) -> list[Violation]:
    """Validate one parsed entry. Returns every violation found (never raises)."""
    v: list[Violation] = []
    raw_id = get_path(entry, "id")
    entry_id = raw_id if isinstance(raw_id, str) and raw_id.strip() else f"<{label}>"

    def add(rule: str, detail: str) -> None:
        v.append(Violation(entry_id, rule, detail))

    # ---- SCHEMA §2: every key required, never omitted -------------------
    for key in REQUIRED_KEYS:
        if get_path(entry, key) is MISSING:
            add("SCHEMA-2-MISSING-KEY", f"required key `{key}` is absent; SCHEMA §2 "
                                        "says write `none` with a reason, never omit a key")
    for key in STRUCTURAL_KEYS:
        if get_path(entry, key) is MISSING:
            add("EXT-STRUCTURAL-MISSING-KEY",
                f"required key `{key}` is absent; SCHEMA v1.0 §4/§7 refuse pairings "
                "the entry must DECLARE, and v1.0 carries no field to declare them in "
                "(builder extension pending a dated addendum)")

    # ---- SCHEMA §6 rule 7: ladder_evidence is computed, never declared ---
    for key in FORBIDDEN_KEYS:
        if get_path(entry, key) is not MISSING:
            add("SCHEMA-6-LADDER-EVIDENCE-NOT-DECLARED",
                f"entry declares `{key}`; SCHEMA §6 makes ladder-evidence a function "
                "of `status` alone, so the generator computes it and an entry may "
                "never assert it")

    # ---- id --------------------------------------------------------------
    if _present(raw_id):
        if not isinstance(raw_id, str) or not ID_RE.match(raw_id):
            add("SCHEMA-2-ID-FORM",
                f"`id` must match ^[a-z0-9_]+$; got {raw_id!r}")
    elif get_path(entry, "id") is not MISSING:
        add("SCHEMA-2-ID-FORM", "`id` is present but empty")

    # ---- family ----------------------------------------------------------
    family = get_path(entry, "family")
    if family is not MISSING:
        fams = family if isinstance(family, list) else [family]
        for f in fams:
            if f not in FAMILIES:
                add("SCHEMA-3-FAMILY",
                    f"`family` must be one of {'/'.join(FAMILIES)}; got {f!r}")

    # ---- flow_class ------------------------------------------------------
    flow_class = get_path(entry, "flow_class")
    if flow_class is not MISSING:
        if not isinstance(flow_class, list) or not flow_class:
            add("SCHEMA-3-FLOW-CLASS",
                "`flow_class` must be a non-empty list from the SCHEMA §3 vocabulary; "
                f"got {flow_class!r}")
        else:
            for fc in flow_class:
                if fc not in FLOW_CLASSES:
                    add("SCHEMA-3-FLOW-CLASS",
                        f"`flow_class` value {fc!r} is not in the SCHEMA §3 controlled "
                        f"vocabulary ({', '.join(FLOW_CLASSES)}); the rung-3 filter reads "
                        "this field, so free text makes an exhaustion claim unrunnable")

    # ---- validation_cases ------------------------------------------------
    cases = get_path(entry, "validation_cases")
    if cases is not MISSING:
        if not isinstance(cases, list) or not cases:
            add("SCHEMA-3-VALIDATION-CASES",
                f"`validation_cases` must be a non-empty list of SCHEMA §3 case ids; "
                f"got {cases!r}")
        else:
            for c in cases:
                if not isinstance(c, str):
                    add("SCHEMA-3-VALIDATION-CASES",
                        f"`validation_cases` entry {c!r} is not a string")
                    continue
                root, _, sub = c.partition(":")
                if root not in VALIDATION_CASE_ROOTS:
                    add("SCHEMA-3-VALIDATION-CASES",
                        f"`validation_cases` id {c!r} does not start from a SCHEMA §3 "
                        f"case root ({', '.join(VALIDATION_CASE_ROOTS)})")
                elif sub and not SUBID_RE.match(sub):
                    add("SCHEMA-3-VALIDATION-CASES",
                        f"`validation_cases` sub-id in {c!r} must match ^[A-Za-z0-9_]+$")

    # ---- free-text placeholders -----------------------------------------
    for key in ("equation_form", "claimed_effect", "install_stanza",
                "contraindications", "what_it_cannot_see",
                "provenance.equations", "provenance.path"):
        val = get_path(entry, key)
        if val is MISSING:
            continue
        if not isinstance(val, str) or not val.strip():
            add("SCHEMA-2-EMPTY-FIELD", f"`{key}` must be a non-empty string; got {val!r}")
        elif _PLACEHOLDER_RE.match(val):
            add("SCHEMA-2-PLACEHOLDER",
                f"`{key}` is a placeholder ({val.strip()!r}), not content")

    # ---- provenance path lives under docs/papers/ ------------------------
    ppath = get_path(entry, "provenance.path")
    if isinstance(ppath, str) and ppath.strip():
        if "docs/papers/" not in ppath:
            add("SCHEMA-2-PROVENANCE-PATH",
                f"`provenance.path` must point under docs/papers/; got {ppath!r}")

    # ---- RULE 1: title_page_verified: yes REQUIRES a non-empty quote -----
    tpv = get_path(entry, "provenance.title_page_verified")
    quote = get_path(entry, "provenance.title_page_quote")
    if tpv is not MISSING:
        if tpv not in ("yes", "no"):
            add("SCHEMA-2-TITLE-PAGE-VERIFIED",
                f"`provenance.title_page_verified` must be `yes` or `no`; got {tpv!r}")
        elif tpv == "yes" and not (isinstance(quote, str) and quote.strip()):
            add("SCHEMA-6-TITLE-PAGE-QUOTE",
                "`provenance.title_page_verified: yes` with an empty "
                "`provenance.title_page_quote`; SCHEMA §6 records this exact defect in "
                "this corpus's own manifest on 2026-09-04 (L-144: never verify by "
                "filename or hash)")

    # ---- status ----------------------------------------------------------
    status = get_path(entry, "status")
    if status is not MISSING and status not in STATUSES:
        add("SCHEMA-6-STATUS-VOCAB",
            f"`status` must be one of {', '.join(STATUSES)}; got {status!r}")

    # ---- RULE 2: REGISTERED or better REQUIRES title-page verification ----
    if status in STATUSES and tpv in ("yes", "no"):
        if tpv != "yes":
            add("SCHEMA-6-REGISTERED-NEEDS-PROVENANCE",
                f"`status: {status}` requires `provenance.title_page_verified: yes`; "
                "SCHEMA §6: capability without provenance is not an entry")

    # ---- install_class ---------------------------------------------------
    install_class = get_path(entry, "install_class")
    if install_class is not MISSING and install_class not in INSTALL_CLASSES:
        add("SCHEMA-4-INSTALL-CLASS",
            f"`install_class` must be one of {', '.join(INSTALL_CLASSES)}; "
            f"got {install_class!r}")

    # ---- RULE 3: fvOptions-source vs an anisotropy correction -------------
    anis = get_path(entry, "structural.modifies_anisotropy_tensor")
    if anis is not MISSING and anis not in ("yes", "no"):
        add("EXT-STRUCTURAL-VOCAB",
            "`structural.modifies_anisotropy_tensor` must be `yes` or `no`; "
            f"got {anis!r}")
    if install_class == "fvOptions-source" and anis == "yes":
        add("SCHEMA-4-FVOPTIONS-ANISOTROPY",
            "`install_class: fvOptions-source` on an entry declaring "
            "`structural.modifies_anisotropy_tensor: yes`; SCHEMA §4: fvOptions adds "
            "sources and CANNOT modify the momentum equation's Reynolds-stress term, "
            "so an anisotropy correction must be `compiled-library`. Wrong on its face")

    # ---- SCHEMA §4: the field-input planted-zero duty ---------------------
    pzv = get_path(entry, "structural.planted_zero_verdict")
    if pzv is not MISSING and pzv not in ("PASS", "FAIL", "none"):
        add("EXT-STRUCTURAL-VOCAB",
            "`structural.planted_zero_verdict` must be PASS, FAIL or none; "
            f"got {pzv!r}")
    if install_class == "field-input" and status in ("IMPLEMENTED", "REPRODUCED"):
        if pzv != "PASS":
            add("SCHEMA-4-FIELD-INPUT-PLANTED-ZERO",
                f"`install_class: field-input` at `status: {status}` with "
                f"`structural.planted_zero_verdict: {pzv!r}`; SCHEMA §4 requires every "
                "field-input entry to plant a non-zero correction field, read it back "
                "and demonstrate the solve moves BEFORE any result from it is believed "
                "(CLAUDE.md rule 3) — a missing field silently becomes zero")

    # ---- SCHEMA §5: libs_route governed by failure_mode -------------------
    failure_mode = get_path(entry, "failure_mode")
    libs_route = get_path(entry, "libs_route")
    justification = get_path(entry, "libs_route_justification")

    if failure_mode is not MISSING and failure_mode not in FAILURE_MODES:
        add("SCHEMA-5-FAILURE-MODE",
            f"`failure_mode` must be `loud` or `silent`; got {failure_mode!r}")
    if libs_route is not MISSING and libs_route not in LIBS_ROUTES:
        add("SCHEMA-5-LIBS-ROUTE",
            f"`libs_route` must be one of {', '.join(LIBS_ROUTES)}; got {libs_route!r}")

    libs_required = get_path(entry, "libs_required")
    if libs_required is not MISSING and not isinstance(libs_required, list):
        add("SCHEMA-2-LIBS-REQUIRED",
            f"`libs_required` must be a list of .so basenames; got {libs_required!r}")

    # RULE 4: failure_mode: silent permits ONLY libs_route: ensure_libs
    if failure_mode == "silent" and libs_route in LIBS_ROUTES and libs_route != "ensure_libs":
        add("SCHEMA-5-SILENT-REQUIRES-ENSURE-LIBS",
            f"`failure_mode: silent` with `libs_route: {libs_route}`; SCHEMA §5 permits "
            "ONLY `ensure_libs` when a failure to load is silent. L-221's cost was five "
            "re-solves returning the unperturbed baseline, which looks like a plausible "
            "physical answer")

    # RULE 5: replace_with_assert REQUIRES a non-`none` justification
    if libs_route == "replace_with_assert":
        if not (isinstance(justification, str) and justification.strip()
                and justification.strip().lower() != "none"):
            add("SCHEMA-5-REPLACE-NEEDS-JUSTIFICATION",
                "`libs_route: replace_with_assert` with "
                f"`libs_route_justification: {justification!r}`; SCHEMA §5 allows it only "
                "with a non-`none` justification naming an ABSENT library (the R4 "
                "precedent), because merging would otherwise load a non-existent .so")

    # ---- RULE 6: `contraindications: none known` must be ARGUED -----------
    contra = get_path(entry, "contraindications")
    if isinstance(contra, str) and contra.strip():
        if _BARE_NONE_RE.match(contra):
            add("SCHEMA-2-CONTRAINDICATIONS-BARE",
                f"`contraindications` is the bare value {contra.strip()!r}; SCHEMA §2: "
                "`none known` must be ARGUED, never defaulted. A correction library "
                "without contraindications is a footgun")
        else:
            lead = _LEADING_NONE_RE.match(contra)
            if lead:
                remainder = contra[lead.end():].strip()
                if len(remainder) < MIN_CONTRA_ARGUMENT_CHARS:
                    add("SCHEMA-2-CONTRAINDICATIONS-BARE",
                        f"`contraindications` opens with {lead.group(1)!r} and carries only "
                        f"{len(remainder)} characters of argument (minimum "
                        f"{MIN_CONTRA_ARGUMENT_CHARS}); SCHEMA §2 requires the claim to be "
                        "argued, not defaulted")

    # `what_it_cannot_see` is the standing honesty clause (charter §16) and may
    # not be a shrug either.
    wics = get_path(entry, "what_it_cannot_see")
    if isinstance(wics, str) and wics.strip() and _BARE_NONE_RE.match(wics):
        add("SCHEMA-2-WHAT-IT-CANNOT-SEE-BARE",
            f"`what_it_cannot_see` is the bare value {wics.strip()!r}; charter §16 makes "
            "this a mandatory statement, and every model has something it cannot see")

    # ---- SCHEMA §7: structural exclusions --------------------------------
    for key, rule, why in (
        ("structural.is_uncertainty_band", "SCHEMA-7-BAND-NOT-A-CORRECTION",
         "SCHEMA §7.1: a band is not a correction. An eigenspace band is a statement "
         "about what the model cannot see; it is never applied to a prediction and "
         "never subtracted from an error (L-219/L-220, D446)"),
        ("structural.is_post_hoc_field_correction", "SCHEMA-7-POST-HOC-NOT-A-MODEL",
         "SCHEMA §7.2: a post-hoc field correction is not a closure model. Entries "
         "modify the solved equations and are re-solved"),
        ("structural.is_per_case_switching", "SCHEMA-7-PER-CASE-SWITCHING",
         "SCHEMA §7.3: per-case switching is not a model. A ladder-derived per-case "
         "correction may never be assembled into a benchmark submission as if it were "
         "one model"),
    ):
        val = get_path(entry, key)
        if val is MISSING:
            continue
        if val not in ("yes", "no"):
            add("EXT-STRUCTURAL-VOCAB", f"`{key}` must be `yes` or `no`; got {val!r}")
        elif val == "yes":
            add(rule, f"entry declares `{key}: yes` — {why}")

    # ---- band_interaction -------------------------------------------------
    band_interaction = get_path(entry, "band_interaction")
    if band_interaction is not MISSING and band_interaction not in BAND_INTERACTIONS:
        add("SCHEMA-2-BAND-INTERACTION",
            f"`band_interaction` must be one of {', '.join(BAND_INTERACTIONS)}; "
            f"got {band_interaction!r}")

    # ---- cost_estimate_core_min ------------------------------------------
    cost = get_path(entry, "cost_estimate_core_min")
    if cost is not MISSING:
        if isinstance(cost, bool) or (isinstance(cost, str) and cost != "none"):
            add("SCHEMA-2-COST-ESTIMATE",
                f"`cost_estimate_core_min` must be a number or the string `none`; "
                f"got {cost!r} (CLAUDE.md rule 12: a proposal with no cost is disqualified)")
        elif isinstance(cost, (int, float)) and cost < 0:
            add("SCHEMA-2-COST-ESTIMATE",
                f"`cost_estimate_core_min` is negative ({cost}); core-minutes are "
                "wall s x ranks / 60 and cannot be negative")

    # ---- equation_form must cite an equation number AND a page ------------
    eqf = get_path(entry, "equation_form")
    if isinstance(eqf, str) and eqf.strip() and not _PLACEHOLDER_RE.match(eqf):
        if UNVERIFIED_TOKEN not in eqf:
            if not (_EQNUM_RE.search(eqf) and _PAGE_RE.search(eqf)):
                add("SCHEMA-2-EQUATION-FORM-UNSOURCED",
                    "`equation_form` cites neither an equation number nor a page; SCHEMA §2 "
                    "requires the modification AT EQUATION LEVEL with its SOURCE EQUATION "
                    "NUMBER and page. If it cannot be transcribed honestly, say so with the "
                    f"token {UNVERIFIED_TOKEN}")
        elif status == "REPRODUCED":
            add("SCHEMA-6-UNVERIFIED-CANNOT-BE-REPRODUCED",
                f"`equation_form` carries {UNVERIFIED_TOKEN} but `status: REPRODUCED`; an "
                "entry whose equation form has not been read cannot have reproduced its "
                "own paper's claim through a registered path (SCHEMA §6)")

    return v


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------
def load_entries(entries_dir: Path):
    """Parse every entries/*.md. Returns (records, violations).

    A record is a dict: {id, entry, source_file, source_sha256}.
    """
    records = []
    violations: list[Violation] = []
    if not entries_dir.is_dir():
        return records, [Violation("<entries>", "SCHEMA-1-NO-ENTRIES-DIR",
                                   f"{entries_dir} does not exist")]
    for path in sorted(entries_dir.glob("*.md")):
        label = path.name
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            violations.append(Violation(f"<{label}>", "SCHEMA-1-IO", str(exc)))
            continue
        try:
            block = split_front_matter(text)
        except ValueError as exc:
            violations.append(Violation(f"<{label}>", "SCHEMA-1-YAML", str(exc)))
            continue
        try:
            parsed = yaml.safe_load(block)
        except yaml.YAMLError as exc:
            violations.append(Violation(f"<{label}>", "SCHEMA-1-YAML",
                                        f"YAML block does not parse: {exc}"))
            continue
        if not isinstance(parsed, dict):
            violations.append(Violation(f"<{label}>", "SCHEMA-1-YAML",
                                        "YAML block is not a mapping of keys"))
            continue
        entry = normalise_scalars(parsed)
        records.append({
            "id": entry.get("id") if isinstance(entry.get("id"), str) else f"<{label}>",
            "entry": entry,
            "source_file": path.name,
            "source_sha256": hashlib.sha256(block.encode("utf-8")).hexdigest(),
            "label": label,
        })
    return records, violations


def validate_all(records) -> list[Violation]:
    violations: list[Violation] = []
    seen: dict[str, str] = {}
    for rec in records:
        violations.extend(validate_entry(rec["entry"], rec["label"]))
        eid = rec["id"]
        if isinstance(eid, str) and ID_RE.match(eid):
            if eid in seen:
                violations.append(Violation(
                    eid, "SCHEMA-1-DUPLICATE-ID",
                    f"id already used by {seen[eid]}; SCHEMA §2 says ladder records cite "
                    "this id, so it must be unique and stable"))
            else:
                seen[eid] = rec["source_file"]
    return violations


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------
def _derive(entry: dict) -> dict:
    """Fields the GENERATOR computes. Never taken from the entry (SCHEMA §6)."""
    status = get_path(entry, "status")
    eqf = get_path(entry, "equation_form")
    return {
        # SCHEMA §6: REPRODUCED is the only state licensed as ladder evidence.
        "ladder_evidence": status == LADDER_EVIDENCE_STATUS,
        # SCHEMA §6: REFUTED-IN-REPRODUCTION is NO as evidence FOR the correction
        # and YES as evidence ABOUT it — a finding, never a discard.
        "evidence_about_correction": status in (
            LADDER_EVIDENCE_STATUS, "REFUTED-IN-REPRODUCTION"),
        "equation_form_unverified": isinstance(eqf, str) and UNVERIFIED_TOKEN in eqf,
    }


def build_library(records) -> dict:
    entries = []
    for rec in sorted(records, key=lambda r: (str(r["id"]), r["source_file"])):
        payload = dict(rec["entry"])
        payload.update(_derive(rec["entry"]))
        payload["source_file"] = f"entries/{rec['source_file']}"
        payload["source_sha256"] = rec["source_sha256"]
        entries.append(payload)
    return {
        "schema_version": SCHEMA_VERSION,
        "builder_extension": BUILDER_EXTENSION,
        "generated_by": "cases/RANS_LES_closure_models/_common/build_correction_library.py",
        "note": ("GENERATED — never hand-edited (SCHEMA §1). `ladder_evidence` is computed "
                 "from `status` by the generator and is never read from an entry (SCHEMA §6). "
                 "No timestamp is emitted so a regeneration is a no-op diff."),
        "entry_count": len(entries),
        "ladder_evidence_count": sum(1 for e in entries if e["ladder_evidence"]),
        "entries": entries,
    }


def render_library(library: dict) -> str:
    return json.dumps(library, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------
# Library directory discovery — so this file can be MOVED without change
# --------------------------------------------------------------------------
def find_library_dir(explicit: str | None = None) -> Path:
    if explicit:
        p = Path(explicit).resolve()
        if not (p / "SCHEMA.md").is_file():
            raise SystemExit(f"build_correction_library: {p}/SCHEMA.md not found")
        return p
    env = os.environ.get("CORRECTION_LIBRARY_DIR")
    if env:
        return find_library_dir(env)
    starts = [Path(__file__).resolve().parent, Path.cwd().resolve()]
    for start in starts:
        for d in [start, *start.parents]:
            cand = d / MARKER
            if cand.is_file():
                return cand.parent
    raise SystemExit(
        "build_correction_library: could not locate docs/closure/correction_library/ "
        "from this script's directory or the working directory; pass --library-dir")


# --------------------------------------------------------------------------
# SELFTEST — planted negative controls (CLAUDE.md rule 3)
# --------------------------------------------------------------------------
def _valid_entry() -> dict:
    """A minimal, schema-valid in-memory entry used as the positive control."""
    return {
        "id": "b_selftest_control_author2026",
        "family": "b",
        "flow_class": ["square_duct_secondary_flow"],
        "validation_cases": ["DUCT:AR_3_Ret_360"],
        "paper_validation_cases": ("Square duct at Re_tau 360; and a ZPG flat plate "
                                   "as the generalisation guard, which this lab holds "
                                   "no on-disk id for."),
        "equation_form": ("tau_ij gains a quadratic term; Eq. (1), p. 1 of the source "
                          "PDF, with C_cr1 = 0.3."),
        "provenance": {
            "path": "docs/papers/closure/Selftest2026_control.pdf",
            "title_page_verified": "yes",
            "title_page_quote": ("\"A Control Entry For The Selftest\" — read off page 1 "
                                 "by lab-lane, 2026-09-04"),
            "equations": "Eq. (1), printed p. 1.",
        },
        "claimed_effect": "\"a control claim\" — abstract, p. 1; 10% error reduction vs DNS.",
        "install_class": "compiled-library",
        "install_stanza": "RAS { RASModel selftestControl; turbulence on; }",
        "model_type_name": "selftestControl",
        "libs_required": ["libselftestTurbulenceModels.so"],
        "libs_route": "ensure_libs",
        "libs_route_justification": "none",
        "failure_mode": "silent",
        "contraindications": ("The paper reports the correction degrades attached "
                              "boundary layers at low Reynolds number, p. 9; treat as "
                              "contraindicated there."),
        "what_it_cannot_see": ("It cannot see history effects; the closure is local in "
                              "the mean-velocity gradient."),
        "band_interaction": "does_not",
        "status": "REGISTERED",
        "cost_estimate_core_min": 120.0,
        "structural": {
            "modifies_anisotropy_tensor": "yes",
            "is_uncertainty_band": "no",
            "is_post_hoc_field_correction": "no",
            "is_per_case_switching": "no",
            "planted_zero_verdict": "none",
        },
    }


def _mutate(base: dict, path: str, value) -> dict:
    """Return a deep-ish copy of base with one dotted path set (or deleted)."""
    out = json.loads(json.dumps(base))
    parts = path.split(".")
    cur = out
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    if value is _DELETE:
        cur.pop(parts[-1], None)
    else:
        cur[parts[-1]] = value
    return out


class _Delete:
    def __repr__(self):
        return "<delete>"


_DELETE = _Delete()


def _selftest_arms():
    """(name, entry, expected_rule or None) — one arm per assertion.

    Every load-bearing rule appears TWICE: once as a valid entry the checker must
    PASS, and once with exactly that rule mutated, which the checker must REFUSE
    with the right message. A checker that cannot be shown to fail is not evidence.
    """
    base = _valid_entry()
    arms = [
        # ---- positive control -------------------------------------------
        ("POS baseline valid entry passes", base, None),

        # ---- RULE 1: title_page_verified yes needs a non-empty quote ------
        ("POS rule1 verified yes WITH quote",
         _mutate(base, "provenance.title_page_quote", "\"Real Title\" — read by X, 2026-09-04"),
         None),
        ("NEG rule1 verified yes with EMPTY quote",
         _mutate(base, "provenance.title_page_quote", "   "),
         "SCHEMA-6-TITLE-PAGE-QUOTE"),
        ("NEG rule1 verified yes with quote key deleted",
         _mutate(base, "provenance.title_page_quote", _DELETE),
         "SCHEMA-6-TITLE-PAGE-QUOTE"),

        # ---- RULE 2: REGISTERED or better needs title-page verification ---
        ("POS rule2 REGISTERED with verified yes", base, None),
        ("NEG rule2 REGISTERED with verified no",
         _mutate(_mutate(base, "provenance.title_page_verified", "no"),
                 "provenance.title_page_quote", "not verified"),
         "SCHEMA-6-REGISTERED-NEEDS-PROVENANCE"),
        ("NEG rule2 REPRODUCED with verified no",
         _mutate(_mutate(_mutate(base, "status", "REPRODUCED"),
                         "provenance.title_page_verified", "no"),
                 "provenance.title_page_quote", "not verified"),
         "SCHEMA-6-REGISTERED-NEEDS-PROVENANCE"),

        # ---- RULE 3: fvOptions-source vs anisotropy ----------------------
        ("POS rule3 fvOptions-source with anisotropy NO",
         _mutate(_mutate(base, "install_class", "fvOptions-source"),
                 "structural.modifies_anisotropy_tensor", "no"),
         None),
        ("POS rule3 compiled-library with anisotropy YES", base, None),
        ("NEG rule3 fvOptions-source with anisotropy YES",
         _mutate(base, "install_class", "fvOptions-source"),
         "SCHEMA-4-FVOPTIONS-ANISOTROPY"),
        ("NEG rule3 structural block missing entirely",
         _mutate(base, "structural", _DELETE),
         "EXT-STRUCTURAL-MISSING-KEY"),

        # ---- RULE 4: failure_mode silent permits ONLY ensure_libs ---------
        ("POS rule4 silent + ensure_libs", base, None),
        ("POS rule4 loud + assert_only",
         _mutate(_mutate(base, "failure_mode", "loud"), "libs_route", "assert_only"),
         None),
        ("NEG rule4 silent + assert_only",
         _mutate(base, "libs_route", "assert_only"),
         "SCHEMA-5-SILENT-REQUIRES-ENSURE-LIBS"),
        ("NEG rule4 silent + replace_with_assert",
         _mutate(_mutate(base, "libs_route", "replace_with_assert"),
                 "libs_route_justification", "libfoo.so is absent from this machine"),
         "SCHEMA-5-SILENT-REQUIRES-ENSURE-LIBS"),

        # ---- RULE 5: replace_with_assert needs a justification ------------
        ("POS rule5 replace_with_assert WITH justification",
         _mutate(_mutate(_mutate(base, "failure_mode", "loud"),
                         "libs_route", "replace_with_assert"),
                 "libs_route_justification",
                 "the replaced entry names libAbsent.so, absent from this machine (R4 precedent)"),
         None),
        ("NEG rule5 replace_with_assert with justification none",
         _mutate(_mutate(base, "failure_mode", "loud"), "libs_route", "replace_with_assert"),
         "SCHEMA-5-REPLACE-NEEDS-JUSTIFICATION"),
        ("NEG rule5 replace_with_assert with EMPTY justification",
         _mutate(_mutate(_mutate(base, "failure_mode", "loud"),
                         "libs_route", "replace_with_assert"),
                 "libs_route_justification", "  "),
         "SCHEMA-5-REPLACE-NEEDS-JUSTIFICATION"),

        # ---- RULE 6: `none known` contraindications must be ARGUED --------
        ("POS rule6 argued contraindication", base, None),
        ("POS rule6 none known WITH a long argument",
         _mutate(base, "contraindications",
                 "None known: the paper tested five separated flows and reported no "
                 "degradation on any of them, and this lab has run none."),
         None),
        ("NEG rule6 bare 'none known'",
         _mutate(base, "contraindications", "none known"),
         "SCHEMA-2-CONTRAINDICATIONS-BARE"),
        ("NEG rule6 bare 'None known.'",
         _mutate(base, "contraindications", "None known."),
         "SCHEMA-2-CONTRAINDICATIONS-BARE"),
        ("NEG rule6 'none known' with a token argument",
         _mutate(base, "contraindications", "none known — no data."),
         "SCHEMA-2-CONTRAINDICATIONS-BARE"),

        # ---- RULE 7: ladder_evidence is computed, never declared ----------
        ("POS rule7 entry does not declare ladder_evidence", base, None),
        ("NEG rule7 entry declares ladder_evidence true",
         _mutate(base, "ladder_evidence", True),
         "SCHEMA-6-LADDER-EVIDENCE-NOT-DECLARED"),
        ("NEG rule7 entry declares ladder_evidence false",
         _mutate(base, "ladder_evidence", False),
         "SCHEMA-6-LADDER-EVIDENCE-NOT-DECLARED"),

        # ---- SCHEMA §7 structural exclusions ------------------------------
        ("NEG s7.1 band declared as an entry",
         _mutate(base, "structural.is_uncertainty_band", "yes"),
         "SCHEMA-7-BAND-NOT-A-CORRECTION"),
        ("NEG s7.2 post-hoc field correction",
         _mutate(base, "structural.is_post_hoc_field_correction", "yes"),
         "SCHEMA-7-POST-HOC-NOT-A-MODEL"),
        ("NEG s7.3 per-case switching",
         _mutate(base, "structural.is_per_case_switching", "yes"),
         "SCHEMA-7-PER-CASE-SWITCHING"),

        # ---- SCHEMA §4 field-input planted-zero duty ----------------------
        ("POS s4 field-input at REGISTERED needs no planted zero yet",
         _mutate(_mutate(_mutate(base, "install_class", "field-input"),
                         "structural.modifies_anisotropy_tensor", "no"),
                 "structural.planted_zero_verdict", "none"),
         None),
        ("NEG s4 field-input at IMPLEMENTED without a planted zero",
         _mutate(_mutate(_mutate(base, "install_class", "field-input"),
                         "structural.modifies_anisotropy_tensor", "no"),
                 "status", "IMPLEMENTED"),
         "SCHEMA-4-FIELD-INPUT-PLANTED-ZERO"),

        # ---- vocabularies and required keys -------------------------------
        ("NEG vocab bad family", _mutate(base, "family", "z"), "SCHEMA-3-FAMILY"),
        ("POS vocab family may be a list (SCHEMA v1.0 says 'one of a..f' — see report)",
         _mutate(base, "family", ["a", "e"]), None),
        ("NEG vocab bad family INSIDE a list",
         _mutate(base, "family", ["a", "z"]), "SCHEMA-3-FAMILY"),
        ("NEG vocab bad flow_class",
         _mutate(base, "flow_class", ["swirling_jet"]), "SCHEMA-3-FLOW-CLASS"),
        ("NEG vocab bad validation_case",
         _mutate(base, "validation_cases", ["MY_OWN_CASE"]), "SCHEMA-3-VALIDATION-CASES"),
        ("NEG vocab bad install_class",
         _mutate(base, "install_class", "magic"), "SCHEMA-4-INSTALL-CLASS"),
        ("NEG vocab bad libs_route",
         _mutate(base, "libs_route", "just_hope"), "SCHEMA-5-LIBS-ROUTE"),
        ("NEG vocab bad failure_mode",
         _mutate(base, "failure_mode", "quiet"), "SCHEMA-5-FAILURE-MODE"),
        ("NEG vocab bad band_interaction",
         _mutate(base, "band_interaction", "maybe"), "SCHEMA-2-BAND-INTERACTION"),
        ("NEG vocab bad status",
         _mutate(base, "status", "VALIDATED"), "SCHEMA-6-STATUS-VOCAB"),
        ("NEG id form uppercase",
         _mutate(base, "id", "B_Selftest"), "SCHEMA-2-ID-FORM"),
        ("NEG missing required key claimed_effect",
         _mutate(base, "claimed_effect", _DELETE), "SCHEMA-2-MISSING-KEY"),
        # SCHEMA Addendum 1 item 3. This arm exists so the key cannot be quietly
        # dropped from REQUIRED_KEYS later without the suite noticing: the clause
        # went UNENFORCED from Addendum 1 until 2026-09-04 precisely because no
        # arm was watching it. A rule with no arm is a rule that can be deleted.
        ("NEG missing required key paper_validation_cases",
         _mutate(base, "paper_validation_cases", _DELETE), "SCHEMA-2-MISSING-KEY"),
        ("NEG cost_estimate is prose",
         _mutate(base, "cost_estimate_core_min", "cheap"), "SCHEMA-2-COST-ESTIMATE"),
        ("POS cost_estimate may be the string none",
         _mutate(base, "cost_estimate_core_min", "none"), None),
        ("NEG provenance path outside docs/papers/",
         _mutate(base, "provenance.path", "/tmp/some_paper.pdf"), "SCHEMA-2-PROVENANCE-PATH"),
        ("NEG equation_form cites no equation or page",
         _mutate(base, "equation_form", "It makes the turbulence better."),
         "SCHEMA-2-EQUATION-FORM-UNSOURCED"),
        ("POS equation_form may declare itself UNVERIFIED",
         _mutate(base, "equation_form",
                 "UNVERIFIED — needs equation-level read; the source paper is not held."),
         None),
        ("NEG UNVERIFIED equation_form cannot be REPRODUCED",
         _mutate(_mutate(base, "equation_form",
                         "UNVERIFIED — needs equation-level read."),
                 "status", "REPRODUCED"),
         "SCHEMA-6-UNVERIFIED-CANNOT-BE-REPRODUCED"),
        ("NEG what_it_cannot_see is a bare shrug",
         _mutate(base, "what_it_cannot_see", "none"),
         "SCHEMA-2-WHAT-IT-CANNOT-SEE-BARE"),
    ]
    return arms


def run_selftest(verbose: bool = True) -> int:
    passed = 0
    failed = []
    arms = _selftest_arms()

    for name, entry, expected in arms:
        vio = validate_entry(entry, "selftest")
        rules = {x.rule for x in vio}
        if expected is None:
            ok = not vio
            detail = "expected NO violations, got: " + ", ".join(
                sorted(x.rule for x in vio)) if vio else ""
        else:
            ok = expected in rules
            detail = (f"expected rule {expected}, got: "
                      + (", ".join(sorted(rules)) if rules else "NO violations at all"))
        if ok:
            passed += 1
        else:
            failed.append((name, detail))
        if verbose:
            print(f"  [{'ok  ' if ok else 'FAIL'}] {name}")
            if not ok:
                print(f"         {detail}")

    # ---- arm: the whole valid SET passes -------------------------------
    n = len(arms)
    base = _valid_entry()
    second = json.loads(json.dumps(base))
    second["id"] = "b_selftest_control_two_author2026"
    recs = [
        {"id": base["id"], "entry": base, "source_file": "a.md",
         "source_sha256": "0" * 64, "label": "a.md"},
        {"id": second["id"], "entry": second, "source_file": "b.md",
         "source_sha256": "1" * 64, "label": "b.md"},
    ]
    n += 1
    if not validate_all(recs):
        passed += 1
        ok = True
    else:
        failed.append(("SET positive control: two valid entries pass",
                       "expected no violations across the set"))
        ok = False
    if verbose:
        print(f"  [{'ok  ' if ok else 'FAIL'}] SET positive control: two valid entries pass")

    # ---- arm: duplicate ids are refused --------------------------------
    dup = [
        {"id": base["id"], "entry": base, "source_file": "a.md",
         "source_sha256": "0" * 64, "label": "a.md"},
        {"id": base["id"], "entry": json.loads(json.dumps(base)), "source_file": "b.md",
         "source_sha256": "1" * 64, "label": "b.md"},
    ]
    n += 1
    ok = any(x.rule == "SCHEMA-1-DUPLICATE-ID" for x in validate_all(dup))
    passed += 1 if ok else 0
    if not ok:
        failed.append(("SET duplicate id refused", "expected SCHEMA-1-DUPLICATE-ID"))
    if verbose:
        print(f"  [{'ok  ' if ok else 'FAIL'}] SET duplicate id refused")

    # ---- arm: ladder_evidence is computed from status, all four states --
    n += 1
    derived = {s: _derive({"status": s, "equation_form": "Eq. (1), p. 1"})["ladder_evidence"]
               for s in STATUSES}
    ok = derived == {"REGISTERED": False, "IMPLEMENTED": False,
                     "REPRODUCED": True, "REFUTED-IN-REPRODUCTION": False}
    passed += 1 if ok else 0
    if not ok:
        failed.append(("GEN ladder_evidence computed from status", f"got {derived}"))
    if verbose:
        print(f"  [{'ok  ' if ok else 'FAIL'}] GEN ladder_evidence computed from status "
              f"(only REPRODUCED is true)")

    # ---- arm: a declared ladder_evidence in the entry is OVERWRITTEN ----
    n += 1
    liar = _valid_entry()
    liar["status"] = "REGISTERED"
    payload = build_library([{"id": liar["id"], "entry": liar, "source_file": "a.md",
                              "source_sha256": "0" * 64, "label": "a.md"}])
    ok = payload["entries"][0]["ladder_evidence"] is False
    passed += 1 if ok else 0
    if not ok:
        failed.append(("GEN generator never trusts an entry's own claim",
                       "REGISTERED entry emitted ladder_evidence true"))
    if verbose:
        print(f"  [{'ok  ' if ok else 'FAIL'}] GEN generator computes ladder_evidence "
              "false for REGISTERED")

    # ---- arm: generation is deterministic (regeneration is a no-op) -----
    n += 1
    a = render_library(build_library(recs))
    b = render_library(build_library(list(reversed(recs))))
    ok = a == b
    passed += 1 if ok else 0
    if not ok:
        failed.append(("GEN deterministic output", "two renderings differ"))
    if verbose:
        print(f"  [{'ok  ' if ok else 'FAIL'}] GEN output deterministic under input reordering")

    # ---- arm: library.json is NOT written when any entry is invalid -----
    n += 1
    ok = _selftest_no_write_on_refusal(verbose)
    passed += 1 if ok else 0
    if not ok:
        failed.append(("IO library.json not written when an entry is invalid",
                       "the builder wrote or altered library.json despite a REFUSE"))

    # ---- arm: the writer is shown able to write (planted control) -------
    n += 1
    ok = _selftest_writer_can_write(verbose)
    passed += 1 if ok else 0
    if not ok:
        failed.append(("IO planted control: the writer CAN write a valid set",
                       "the no-write arm above would be meaningless"))

    print()
    print(f"SELFTEST: {passed}/{n} arms passed")
    if failed:
        print("SELFTEST FAILURES:")
        for name, detail in failed:
            print(f"  - {name}: {detail}")
        return 2
    return 0


def _write_temp_library(tmp: Path, entry_texts) -> tuple[int, Path]:
    """Build a throwaway library dir, run the pipeline, return (rc, library.json)."""
    (tmp / "entries").mkdir(parents=True, exist_ok=True)
    (tmp / "SCHEMA.md").write_text("selftest marker\n", encoding="utf-8")
    for name, entry in entry_texts:
        body = yaml.safe_dump(entry, sort_keys=True, allow_unicode=True,
                              default_flow_style=False)
        (tmp / "entries" / name).write_text(
            f"---\n{body}---\n\nselftest prose, never parsed.\n", encoding="utf-8")
    rc = run_pipeline(tmp, write=True, quiet=True)
    return rc, tmp / "library.json"


def _selftest_no_write_on_refusal(verbose: bool) -> bool:
    """PLANTED CONTROL: with one invalid entry present, library.json must not be
    written at all, and an EXISTING library.json must be left byte-identical."""
    import tempfile

    bad = _valid_entry()
    bad["id"] = "b_selftest_bad_author2026"
    bad["contraindications"] = "none known"          # rule 6 violation
    good = _valid_entry()

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        sentinel = "{\"sentinel\": \"pre-existing library.json\"}\n"
        (tmp / "entries").mkdir(parents=True)
        (tmp / "SCHEMA.md").write_text("selftest marker\n", encoding="utf-8")
        (tmp / "library.json").write_text(sentinel, encoding="utf-8")
        for name, entry in (("good.md", good), ("bad.md", bad)):
            body = yaml.safe_dump(entry, sort_keys=True, allow_unicode=True,
                                  default_flow_style=False)
            (tmp / "entries" / name).write_text(
                f"---\n{body}---\n\nprose\n", encoding="utf-8")
        rc = run_pipeline(tmp, write=True, quiet=True)
        after = (tmp / "library.json").read_text(encoding="utf-8")
        ok = (rc == 2) and (after == sentinel)
    if verbose:
        print(f"  [{'ok  ' if ok else 'FAIL'}] IO library.json NOT written (and an "
              "existing one untouched) when any entry is invalid")
    return ok


def _selftest_writer_can_write(verbose: bool) -> bool:
    """PLANTED CONTROL for the control above: the same writer, on a set with no
    violations, MUST produce a library.json. A refusal-to-write that cannot be
    shown to write is not evidence (CLAUDE.md rule 3)."""
    import tempfile

    good = _valid_entry()
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        rc, lib = _write_temp_library(tmp, [("good.md", good)])
        ok = rc == 0 and lib.is_file() and json.loads(lib.read_text())["entry_count"] == 1
    if verbose:
        print(f"  [{'ok  ' if ok else 'FAIL'}] IO planted control: the same writer DOES "
              "write library.json for a valid set")
    return ok


# --------------------------------------------------------------------------
# Pipeline
# --------------------------------------------------------------------------
def run_pipeline(library_dir: Path, write: bool, quiet: bool = False) -> int:
    entries_dir = library_dir / "entries"
    records, violations = load_entries(entries_dir)
    violations = violations + validate_all(records)

    if violations:
        if not quiet:
            for vio in sorted(violations, key=lambda x: (x.entry_id, x.rule, x.detail)):
                print(vio.render())
            print()
            print(f"REFUSED: {len(violations)} violation(s) across {len(records)} entry "
                  f"file(s). library.json NOT written.")
        return 2

    if not records:
        if not quiet:
            print(f"REFUSE: <entries>: SCHEMA-1-NO-ENTRIES — {entries_dir} holds no "
                  "*.md entry files; refusing to write an empty library.json")
        return 2

    library = build_library(records)
    text = render_library(library)
    target = library_dir / "library.json"
    if write:
        previous = target.read_text(encoding="utf-8") if target.is_file() else None
        if previous == text:
            if not quiet:
                print(f"OK: {len(records)} entr(y/ies) valid. {target} already current "
                      "(regeneration is a no-op diff).")
        else:
            target.write_text(text, encoding="utf-8")
            if not quiet:
                print(f"OK: {len(records)} entr(y/ies) valid. Wrote {target}.")
    elif not quiet:
        print(f"OK: {len(records)} entr(y/ies) valid. --check: library.json not written.")

    if not quiet:
        n_ev = library["ladder_evidence_count"]
        print(f"     ladder_evidence (status REPRODUCED only): {n_ev} of {len(records)}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Validate closure-correction library entries against SCHEMA.md v1.0 "
                    "and generate library.json.")
    ap.add_argument("--library-dir", default=None,
                    help="docs/closure/correction_library (auto-discovered if omitted)")
    ap.add_argument("--check", action="store_true",
                    help="validate only; never write library.json")
    ap.add_argument("--selftest", action="store_true",
                    help="run the planted negative controls and exit")
    args = ap.parse_args(argv)

    if args.selftest:
        print("build_correction_library --selftest")
        print(f"  contract: SCHEMA.md v{SCHEMA_VERSION} (FROZEN); "
              f"builder extension {BUILDER_EXTENSION}")
        print("  every load-bearing rule is asserted twice: a valid entry the checker "
              "must PASS,")
        print("  and exactly that rule mutated, which the checker must REFUSE.")
        print()
        return run_selftest()

    library_dir = find_library_dir(args.library_dir)
    return run_pipeline(library_dir, write=not args.check)


if __name__ == "__main__":
    raise SystemExit(main())
