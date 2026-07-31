"""The Certonomous Certificate — a one-page, sealed record of a solve.

Every completed mission can issue a single-page PDF that states the geometry,
the objective, the measured result with its envelope, the trust tier, the three
V&V-20 uncertainty channels, the compute spent, and an evidence-bundle SHA-256
seal.  The seal is a hash over the substantive facts of the run: change any
recorded number and the hash no longer matches, so the certificate is
tamper-evident without a signing key.

Pure standard library.  The PDF is written by hand — a single page, the two
built-in Helvetica faces (no font embedding), text, rules, and filled badges —
so nothing here needs reportlab or any third-party PDF toolkit on the
controller.  Text is emitted in WinAnsi so ``±``, ``°`` and ``×`` render; a few
maths glyphs that WinAnsi lacks are folded to ASCII first, and an em dash is
never emitted on the sealed page.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable

# A4 portrait, in PostScript points.
_PAGE_W, _PAGE_H = 595.28, 841.89
_MARGIN = 56.0

# Ink palette (0..1 RGB).
_INK = (0.11, 0.14, 0.19)
_MUTED = (0.42, 0.46, 0.51)
_RULE = (0.86, 0.88, 0.91)
_WHITE = (1.0, 1.0, 1.0)
_SEAL = (0.20, 0.24, 0.30)

# Trust-tier badge colours.
_TIER_COLOR = {
    "VALIDATED": (0.13, 0.55, 0.33),
    "SOLVER-BACKED": (0.24, 0.51, 0.82),
    "RESEARCH MODEL": (0.80, 0.53, 0.11),
    "TREND ONLY": (0.80, 0.53, 0.11),  # legacy records
    "NEEDS WORK": (0.72, 0.20, 0.20),
}
_DEFAULT_TIER_COLOR = (0.42, 0.46, 0.51)

# Legacy tier names normalize onto the current fidelity chips before display.
_LEGACY_TIER_ALIAS = {"TREND ONLY": "SOLVER-BACKED",
                      "REFERENCE REGIME MISMATCH": "SOLVER-BACKED",
                      "NEEDS WORK": "UNCONVERGED",
                      "CONCEPTUAL MODEL": "RESEARCH MODEL"}


def _resolved_tier(tier: str) -> str:
    return _LEGACY_TIER_ALIAS.get(tier, tier)

# WinAnsi cannot encode these; fold to something it can before laying out text.
# The em dash is foldable in WinAnsi but banned from the sealed page outright.
# The middle dot "·" is NOT folded: WinAnsi encodes it (0xB7) and it is the
# certificate's section separator, rendered as intended.
_GLYPH_FOLD = {
    "≈": "~", "≥": ">=", "≤": "<=", "−": "-",
    "—": "-", "–": "-", "‑": "-", "→": "->",
    "“": '"', "”": '"', "‘": "'", "’": "'",
}

# Language rails for the sealed page: no storage narration, no retired TREND
# label, no "real solve" phrasing (the platform says "selected solver").
# These rewrite wording only, applied at render time; the evidence seal is
# computed over the caller's facts upstream and no number is ever touched.
_BANNED_LANGUAGE = (
    (re.compile(r"\bTREND[ -]ONLY\b", re.IGNORECASE), "SOLVER-BACKED"),
    (re.compile(r"\bTREND\b"), "SOLVER-BACKED"),
    (re.compile(r"\breal[ -]solves\b", re.IGNORECASE), "selected-solver runs"),
    (re.compile(r"\breal[ -]solve\b", re.IGNORECASE), "selected-solver run"),
    (re.compile(r"\bpre[ -]?computed\b", re.IGNORECASE), "prior"),
    (re.compile(r"\bcached\b", re.IGNORECASE), "held"),
    (re.compile(r"\bstored\b", re.IGNORECASE), "held"),
    (re.compile(r"\bsaved\b", re.IGNORECASE), "held"),
    (re.compile(r"\brecorded\b", re.IGNORECASE), "documented"),
    (re.compile(r"\bdemos?\b", re.IGNORECASE), "presentation"),
    # Internal study identifiers and tool names never reach the sealed page.
    # These delete or rename jargon only; no number is ever touched.
    (re.compile(r"[;,]?\s*\bstudy\s+uq-[\w,\s-]+", re.IGNORECASE), ""),
    (re.compile(r"[;,]?\s*\buq-[\w-]+-r\d+\b", re.IGNORECASE), ""),
    (re.compile(r"\bcheckMesh\b", re.IGNORECASE), "mesh check"),
)

# Channel-line render rails, applied to every uncertainty-channel line before
# it is drawn (defense in depth over the workflow-side wording).  Rails DELETE
# jargon — internal uq-study slugs, tool names — and never alter a value:
# every number that survives renders verbatim.
_STUDY_REF = re.compile(r"[;,]?\s*\bstudy\s+uq-[\w,\s-]+", re.IGNORECASE)
_UQ_SLUG = re.compile(r"[;,]?\s*\buq-[\w-]+-r\d+\b", re.IGNORECASE)
_TOOL_NAME = re.compile(r"\bcheckMesh\b:?\s*", re.IGNORECASE)
# The sealed page never states a UQ method by name (owner rule, 2026-07-24):
# named procedures fold to the generic register — a citation is deleted, a
# named estimator becomes its plain description. Wording only; every number
# in the surrounding text renders verbatim.
_METHOD_GENERIC = (
    (re.compile(r"\s*\((?:Eca|Eça)\s*(?:&|and)\s*Hoekstra[^)]*\)",
                re.IGNORECASE), ""),
    (re.compile(r"\b(?:Eca|Eça)\s*(?:&|and)\s*Hoekstra(?:\s*,?\s*\d{4})?",
                re.IGNORECASE), "the default numerical consistency method"),
    (re.compile(r"\bMonte[- ]Carlo\b", re.IGNORECASE), "ensemble"),
    (re.compile(r"\bleast[- ]squares fit\b", re.IGNORECASE),
     "default numerical consistency method"),
    (re.compile(r"\bleast[- ]squares\b", re.IGNORECASE),
     "default numerical consistency"),
    (re.compile(r"\bGCI\b"), "grid-refinement"),
    # The k-rung spec is a level index list, not a measured value; the
    # sanctioned generic phrasing drops it with the method name.
    (re.compile(r"\bphase-quadrature ladder(?:\s+k\s*=\s*[\d/]+)?",
                re.IGNORECASE),
     "multi-level refinement of the cycle evaluation"),
    (re.compile(r"\bquadrature ladder(?:\s+k\s*=\s*[\d/]+)?", re.IGNORECASE),
     "multi-level refinement"),
)
_INPUT_ASSUMED = "No input uncertainty was assumed for this problem."
_INPUT_ASSUMED_HINTS = ("as specified exactly", "no input spread")


def _channel_rails(text: str) -> str:
    """Strip internal identifiers, tool jargon, and named UQ methods from one
    channel line. Wording only; every number passes through verbatim."""
    s = _STUDY_REF.sub("", text)
    s = _UQ_SLUG.sub("", s)
    s = _TOOL_NAME.sub("", s)
    for pattern, replacement in _METHOD_GENERIC:
        s = pattern.sub(replacement, s)
    s = re.sub(r"\(\s*\)", "", s)            # a deleted citation leaves no ()
    s = re.sub(r"\s+([;,.])", r"\1", s)      # no space left before punctuation
    s = re.sub(r"[;,]\s*([;,])", r"\1", s)   # collapse doubled separators
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip(" ;,")


# A channel note that joins several sentences or bullets inline renders one
# per line: split at bullet markers and at sentence ends, never inside a
# number or a parenthetical clause. Wording only; every number is untouched.
_NOTE_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+(?=\S)")


def _note_lines(note: str) -> list[str]:
    """One rendered line per bullet/sentence of a channel note, each starting
    with a capital letter. Values pass through verbatim."""
    parts: list[str] = []
    for chunk in re.split(r"\s*•\s*", note):
        for piece in _NOTE_SENTENCE_BREAK.split(chunk):
            piece = piece.strip()
            if piece:
                parts.append(piece[:1].upper() + piece[1:])
    return parts or [note]


def _channel_fields(ch: dict) -> tuple[str, str, bool, str]:
    """(name, value, quantified, note) for one channel, railed for render.

    An unquantified input channel whose text narrates the freestream taken
    "as specified exactly" (no input spread propagated) renders as the single
    plain sentence ``No input uncertainty was assumed for this problem.``; a
    note already in that form passes through unchanged.
    """
    quantified = bool(ch.get("quantified"))
    name = _channel_rails(str(ch.get("name", "")))
    value = str(ch.get("value", "")) if ch.get("value") is not None else "-"
    note = str(ch.get("note") or "")
    if (not quantified and name.strip().lower().startswith("input")
            and (note.strip() == _INPUT_ASSUMED
                 or any(hint in note for hint in _INPUT_ASSUMED_HINTS))):
        note = _INPUT_ASSUMED
    else:
        note = _channel_rails(note)
    return name, value, quantified, note


# --------------------------------------------------------------------------
# Minimal PDF canvas
# --------------------------------------------------------------------------

class _Canvas:
    """Accumulate drawing operators, then serialise to PDF bytes.

    One page is the norm and stays byte-for-byte what it always was. A
    certificate that carries a full constraint list and an assumed-values
    ledger can outgrow a single leaf, so ``new_page`` starts a second: the
    operators simply move to a fresh stream and the document grows a page.
    """

    def __init__(self) -> None:
        self._ops: list[str] = []
        self._done: list[list[str]] = []

    def new_page(self) -> None:
        """Close the current page and start drawing on the next one."""
        self._done.append(self._ops)
        self._ops = []

    @property
    def page_count(self) -> int:
        return len(self._done) + 1

    # -- primitives --------------------------------------------------------
    def text(self, x: float, y: float, s: str, size: float = 10.0,
             bold: bool = False, color=_INK, serif: bool = False) -> None:
        if serif:
            font = "F4" if bold else "F3"
        else:
            font = "F2" if bold else "F1"
        r, g, b = color
        self._ops.append(
            f"BT /{font} {size:.2f} Tf {r:.3f} {g:.3f} {b:.3f} rg "
            f"1 0 0 1 {x:.2f} {y:.2f} Tm ({_escape(s)}) Tj ET")

    def rule(self, x1: float, y: float, x2: float, width: float = 0.7,
             color=_RULE) -> None:
        r, g, b = color
        self._ops.append(
            f"{width:.2f} w {r:.3f} {g:.3f} {b:.3f} RG "
            f"{x1:.2f} {y:.2f} m {x2:.2f} {y:.2f} l S")

    def rect(self, x: float, y: float, w: float, h: float, fill) -> None:
        r, g, b = fill
        self._ops.append(
            f"{r:.3f} {g:.3f} {b:.3f} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f")

    # -- serialise ---------------------------------------------------------
    def to_pdf(self) -> bytes:
        pages = [*self._done, self._ops]
        streams = ["\n".join(ops).encode("cp1252", "replace") for ops in pages]
        # Object numbering: 1 catalog, 2 page tree, then one page object and
        # one content stream per leaf, then the four fonts.
        n = len(streams)
        page_ids = [3 + 2 * i for i in range(n)]
        font_first = 3 + 2 * n
        kids = " ".join(f"{i} 0 R" for i in page_ids)
        objects: list[bytes] = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            (f"<< /Type /Pages /Kids [{kids}] /Count {n} >>").encode("ascii"),
        ]
        for i, content in enumerate(streams):
            objects.append(
                (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {_PAGE_W:.2f} "
                 f"{_PAGE_H:.2f}] /Resources << /Font << "
                 f"/F1 {font_first} 0 R /F2 {font_first + 1} 0 R "
                 f"/F3 {font_first + 2} 0 R /F4 {font_first + 3} 0 R >> >> "
                 f"/Contents {page_ids[i] + 1} 0 R >>").encode("ascii"))
            objects.append(
                b"<< /Length " + str(len(content)).encode("ascii")
                + b" >>\nstream\n" + content + b"\nendstream")
        objects += [
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
            b"/Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
            b"/Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman "
            b"/Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Bold "
            b"/Encoding /WinAnsiEncoding >>",
        ]
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets: list[int] = []
        for i, body in enumerate(objects, start=1):
            offsets.append(len(out))
            out += f"{i} 0 obj\n".encode("ascii") + body + b"\nendobj\n"
        xref_pos = len(out)
        out += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
        out += b"0000000000 65535 f \n"
        for off in offsets:
            out += f"{off:010d} 00000 n \n".encode("ascii")
        out += (f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                f"startxref\n{xref_pos}\n%%EOF\n").encode("ascii")
        return bytes(out)


def _fold(s: str) -> str:
    for bad, good in _GLYPH_FOLD.items():
        s = s.replace(bad, good)
    for pattern, replacement in _BANNED_LANGUAGE:
        s = pattern.sub(replacement, s)
    return s


def _escape(s: str) -> str:
    s = _fold(s)
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _avg_width(size: float) -> float:
    # Helvetica averages ~0.52 em across running text; enough for wrapping.
    return 0.52 * size


def _looks_like_interval(env_text: str) -> bool:
    """Is this envelope actually a plus-or-minus interval?

    Conservative on purpose. The cost of a false positive is a sealed
    certificate claiming a 95% confidence interval the run never computed; the
    cost of a false negative is only that a genuine interval prints its own
    text instead of carrying the CI caption. So this returns True only for
    something that reads as a magnitude and nothing else: a bare number, with
    an optional unit or percent sign, and no prose.

    Rejected by design: "converged at iteration 1,734", "5% pass threshold",
    "this case's own recipe", "at the design condition", "non-orthogonality
    40.5 vs 70 gate", "0.029620 to 0.021245 at C_L 0.5". The last one is the
    case that prompted this: a range of drag values, printed as if it were a
    confidence interval on a percentage.
    """
    t = env_text.strip()
    if not t:
        return False
    # One number, optionally signed, optionally with a unit, and nothing else.
    # Anchoring the whole string is what does the work: any trailing prose
    # fails the match, so no sentence can be mistaken for a magnitude.
    return bool(re.fullmatch(
        r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?"
        r"\s*(?:%|deg|rad|m|mm|cm|km|s|ms|Pa|kPa|kg|N|m/s|m2|m\^2)?", t))


def _wrap(text: str, size: float, max_width: float) -> list[str]:
    words = _fold(text).split()
    if not words:
        return [""]
    lines: list[str] = []
    line = words[0]
    for word in words[1:]:
        if (len(line) + 1 + len(word)) * _avg_width(size) <= max_width:
            line = f"{line} {word}"
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


# --------------------------------------------------------------------------
# Evidence seal
# --------------------------------------------------------------------------

def evidence_hash(payload: dict) -> str:
    """SHA-256 over the substantive facts, canonicalised so it is reproducible."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                           default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _seal_payload(*, mission_id, geometry, objective, results, channels,
                  compute, issued_utc, mesh=None, result_fields=None,
                  scope=None, constraints=None, assumptions=None) -> dict:
    """The exact fields the seal covers — nothing cosmetic, everything factual.

    ``mesh`` (the mission's actual checkMesh facts) and ``result_fields`` (the
    structured parameter/value pairs of the result block) join the payload only
    when the caller supplies them, so certificates without them keep their
    seals.
    """
    payload = {
        "mission_id": mission_id,
        "geometry": geometry,
        "objective": objective,
        "issued_utc": issued_utc,
        "results": [
            {k: r.get(k) for k in ("quantity", "value", "envelope", "tier", "reason")}
            for r in results
        ],
        "channels": [
            {k: c.get(k) for k in ("name", "value", "quantified", "note")}
            for c in (channels or [])
        ],
        "compute": compute or {},
    }
    if mesh:
        payload["mesh"] = dict(mesh)
    if result_fields:
        payload["result_fields"] = [[label, value] for label, value in result_fields]
    if scope:
        payload["scope"] = scope
    if constraints:
        payload["constraints"] = [list(row) for row in constraints]
    if assumptions:
        payload["assumptions"] = [list(row) for row in assumptions]
    return payload


def _normalized_triples(raw) -> list[tuple[str, str, str]]:
    """Ordered (name, value, tag) rows from whatever shape the caller holds.

    The same contract as ``_normalized_result_fields``: sequences or dicts in,
    verbatim strings out. A row missing its third column keeps an empty tag
    rather than being dropped, because a constraint with no tag is still a
    constraint the run applied.
    """
    rows: list[tuple[str, str, str]] = []
    for item in raw or ():
        if isinstance(item, dict):
            cells = [item.get("name"), item.get("value"), item.get("tag")]
        else:
            try:
                cells = list(item)
            except TypeError:
                continue
        cells += [""] * (3 - len(cells))
        name, value, tag = cells[0], cells[1], cells[2]
        if name is None or value is None:
            continue
        rows.append((str(name), str(value), "" if tag is None else str(tag)))
    return rows


def _normalized_result_fields(raw) -> list[tuple[str, str]]:
    """Ordered (label, value) pairs from whatever shape the caller holds.

    Accepts pairs/lists or {"label", "value"} dicts. Labels and values render
    verbatim — a label like "AR" or "L/D" is never re-cased, and no value is
    ever reformatted.
    """
    fields: list[tuple[str, str]] = []
    for item in raw or ():
        if isinstance(item, dict):
            label, value = item.get("label"), item.get("value")
        else:
            try:
                label, value = item[0], item[1]
            except (TypeError, IndexError, KeyError):
                continue
        if label is None or value is None:
            continue
        fields.append((str(label), str(value)))
    return fields


def _write_pdf_atomic(out_path: str | Path, data: bytes) -> Path:
    """Write the page to a staging file, then move it into place in one step.

    The served path therefore always holds either the previous complete page
    or the new complete page — a reader can never be handed a half-written
    certificate, and a rerun replaces the file in a single atomic swap.
    """
    out_path = Path(out_path).with_suffix(".pdf")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    staging = out_path.with_name(out_path.name + ".tmp")
    staging.write_bytes(data)
    os.replace(staging, out_path)
    return out_path


# --------------------------------------------------------------------------
# Certificate layout
# --------------------------------------------------------------------------

def build_certificate(report_doc: dict, *, out_path: str | Path,
                      geometry: str, objective: str, mission_id: str,
                      issued_utc: str, channels: Iterable[dict] | None = None
                      ) -> dict[str, Any]:
    """Render one certificate PDF for a finished mission; return its seal record.

    ``report_doc`` is the :func:`lab_report` dict.  ``channels`` is the list of
    V&V-20 uncertainty channels if the mission produced them; when absent the
    certificate falls back to the report's plain-language uncertainty notes.
    Returns ``{"path", "hash", "mission_id", "tier"}``.
    """
    results = list(report_doc.get("results", []))
    # uncertainty_channels() hands back {"channels": [...]}; accept either that
    # or a bare list so callers can pass whichever they hold.
    if isinstance(channels, dict):
        channels = channels.get("channels", [])
    channels = [c for c in (channels or []) if isinstance(c, dict)]
    compute = report_doc.get("compute", {})
    primary = results[0] if results else {}
    tier = (primary.get("tier") or "").upper()

    seal = evidence_hash(_seal_payload(
        mission_id=mission_id, geometry=geometry, objective=objective,
        results=results, channels=channels, compute=compute,
        issued_utc=issued_utc))

    c = _Canvas()
    left = _MARGIN
    right = _PAGE_W - _MARGIN
    width = right - left
    y = _PAGE_H - _MARGIN

    # -- masthead ----------------------------------------------------------
    c.text(left, y - 16, "CERTONOMOUS", size=22, bold=True, color=_INK)
    c.text(right - 180, y - 12, "Certificate of Autonomous Solve",
           size=8.5, bold=True, color=_MUTED)
    c.text(right - 180, y - 24, f"Mission {mission_id}", size=8.5, color=_MUTED)
    y -= 34
    c.rule(left, y, right, width=1.1, color=_INK)
    y -= 26

    # -- identity fields ---------------------------------------------------
    for label, value in (("Geometry", geometry), ("Objective", objective),
                         ("Issued (UTC)", issued_utc)):
        c.text(left, y, label, size=8, bold=True, color=_MUTED)
        for line in _wrap(value, 11, width - 96):
            c.text(left + 96, y, line, size=11, color=_INK)
            y -= 15
        y -= 5
    y -= 8

    # -- headline result + trust badge ------------------------------------
    if primary:
        c.text(left, y, "Result", size=8, bold=True, color=_MUTED)
        y -= 20
        headline = f"{primary.get('quantity', 'Result')}   {primary.get('value', '')}"
        c.text(left, y, headline, size=17, bold=True, color=_INK)
        # SOLVER-BACKED is the unlabeled default for this simulation platform:
        # a real solve with no further chip renders no badge at all.
        shown_tier = _resolved_tier(tier)
        if shown_tier and shown_tier != "SOLVER-BACKED":
            badge = _TIER_COLOR.get(shown_tier, _DEFAULT_TIER_COLOR)
            badge_w = max(78.0, len(shown_tier) * 6.6 + 20)
            c.rect(right - badge_w, y - 4, badge_w, 20, fill=badge)
            c.text(right - badge_w + 10, y + 1.5, shown_tier,
                   size=9.5, bold=True, color=_WHITE)
        y -= 18
        env = primary.get("envelope")
        if env:
            c.text(left, y, f"Envelope: {env}", size=10, color=_MUTED)
            y -= 15
        reason = primary.get("reason")
        if reason:
            for line in _wrap(f"Trust basis: {reason}", 10, width):
                c.text(left, y, line, size=10, color=_MUTED)
                y -= 14
        y -= 6

    # secondary results (lift, mesh, ...)
    for item in results[1:]:
        c.text(left, y, str(item.get("quantity", "")), size=9.5, bold=True,
               color=_INK)
        val = str(item.get("value", ""))
        env = item.get("envelope")
        c.text(left + 150, y, f"{val}   {env}" if env else val, size=9.5,
               color=_MUTED)
        y -= 15
    y -= 10
    c.rule(left, y, right)
    y -= 22

    # -- V&V uncertainty channels -----------------------------------------
    c.text(left, y, "Uncertainty", size=8, bold=True, color=_MUTED)
    y -= 18
    if channels:
        for ch in channels:
            name, value, quantified, note = _channel_fields(ch)
            state = "quantified" if quantified else "not quantified"
            c.text(left, y, name, size=9.5, bold=True, color=_INK)
            c.text(left + 130, y, value, size=9.5, color=_INK)
            c.text(left + 230, y, f"({state})", size=9,
                   color=_MUTED if quantified else _DEFAULT_TIER_COLOR)
            y -= 13
            if note:
                for sentence in _note_lines(note):
                    for line in _wrap(sentence, 8.5, width - 12):
                        c.text(left + 12, y, line, size=8.5, color=_MUTED)
                        y -= 11
            y -= 4
    else:
        for line_txt in report_doc.get("uncertainty", [])[:3]:
            for line in _wrap(_channel_rails(str(line_txt)), 9, width):
                c.text(left, y, line, size=9, color=_MUTED)
                y -= 12
            y -= 3
    y -= 6

    # -- compute line ------------------------------------------------------
    # Mirrors ComputeLedger.as_dict(): spent/saved core-minutes and the
    # full-fidelity flag. A cell count, when carried on the compute dict, leads.
    compute_bits = []
    if compute.get("cells"):
        compute_bits.append(f"{compute['cells']:,} cells" if isinstance(
            compute.get("cells"), int) else str(compute["cells"]))
    spent = compute.get("spent_core_minutes", compute.get("core_minutes"))
    if spent is not None:
        compute_bits.append(f"{spent} core-min spent")
    saved = compute.get("saved_core_minutes")
    if saved:
        compute_bits.append(f"{saved} core-min avoided")
    if compute.get("full_fidelity"):
        compute_bits.append("full fidelity")
    if compute_bits:
        c.rule(left, y, right)
        y -= 16
        c.text(left, y, "Compute", size=8, bold=True, color=_MUTED)
        c.text(left + 96, y, "   ·   ".join(compute_bits), size=9.5, color=_INK)
        y -= 20

    # -- evidence seal -----------------------------------------------------
    seal_h = 58
    c.rect(left, _MARGIN + 30, width, seal_h, fill=(0.96, 0.97, 0.98))
    sy = _MARGIN + 30 + seal_h - 16
    c.text(left + 12, sy, "Evidence Seal  ·  SHA-256", size=8, bold=True,
           color=_SEAL)
    sy -= 16
    c.text(left + 12, sy, seal[:32], size=9.5, bold=True, color=_SEAL)
    c.text(left + 12, sy - 12, seal[32:], size=9.5, bold=True, color=_SEAL)

    # -- footer ------------------------------------------------------------
    c.text(left, _MARGIN + 12,
           "Sealed by the hash above; any change to the documented run invalidates it. "
           "VALIDATED is earned only against a published experiment.",
           size=7.5, color=_MUTED)

    out_path = _write_pdf_atomic(out_path, c.to_pdf())
    return {"path": str(out_path), "hash": seal, "mission_id": mission_id,
            "tier": tier}


# --------------------------------------------------------------------------
# Certificate — redesign (v2), PROPOSAL. Not the default until signed off.
# --------------------------------------------------------------------------

# Fidelity chip (orchestrator G5 semantics). Reserved, icon-free colours.
_FIDELITY_COLOR = {
    "VALIDATED": (0.13, 0.55, 0.33),
    "SOLVER-BACKED": (0.16, 0.40, 0.66),
    "RESEARCH MODEL": (0.66, 0.45, 0.10),
}
_DEFAULT_FIDELITY_COLOR = (0.42, 0.46, 0.51)

# Minimal display-name fallback until GUI-2's display_names registry lands.
_DISPLAY_NAME_FALLBACK = {
    "b52": "B-52 Stratofortress-class airframe",
    "motorbike": "Motorcycle-and-rider body",
    "ahmed_25": "Ahmed reference body (25 deg slant)",
    "ahmed_35": "Ahmed reference body (35 deg slant)",
    "cube": "Cube",
    "sphere": "Sphere",
    "cylinder": "Circular cylinder",
}


def display_name_for(geometry: str, explicit: str | None = None) -> str:
    """Human display name for the subject geometry (never a file-facing slug)."""
    if explicit:
        return explicit
    try:  # prefer GUI-2's registry when it lands
        from . import display_names  # type: ignore
        resolved = display_names.display_name(geometry)  # type: ignore
        if resolved:
            return resolved
    except Exception:
        pass
    key = str(geometry).strip().lower().replace("-", "").replace(" ", "")
    return _DISPLAY_NAME_FALLBACK.get(key, str(geometry))


def _human_number(mission_id: str, issued_utc: str, seal: str) -> str:
    """A human certificate number C-YYYY-NNNN, deterministic from the seal.

    Never the mission slug — the slug is metadata, this is the certificate's
    own registered identity.
    """
    year = (issued_utc or "2026")[:4]
    if not (len(year) == 4 and year.isdigit()):
        year = "2026"
    n = int(seal[:6], 16) % 10000 if seal else 0
    return f"C-{year}-{n:04d}"


def _infer_fidelity(tier: str, compute: dict, results: list) -> str:
    if tier == "VALIDATED":
        return "VALIDATED"
    text = " ".join(str(r.get("reason", "")) for r in results).lower()
    conceptual = any(w in text for w in
                     ("conceptual", "reduced-order", "orifice model",
                      "sizing model", "not a solved flow"))
    if conceptual:
        return "RESEARCH MODEL"
    return "SOLVER-BACKED"


def _mesh_rows(mesh: dict) -> list[tuple[str, str, str, bool]]:
    """(check, measured, verdict, ok) rows for the mesh-validity block.

    Gates default to the OpenFOAM guidance the studies already judge by:
    70 degrees max non-orthogonality (hard gate), 4.0 max skewness (guidance).
    A value the mesh check did not report renders as exactly that; no number
    is ever invented for the page, and no tool name reaches it.
    """
    rows: list[tuple[str, str, str, bool]] = []
    cells = mesh.get("cells")
    if cells is not None:
        rows.append(("Cells", f"{int(cells):,}", "", True))
    non_ortho = mesh.get("max_non_orthogonality")
    gate = float(mesh.get("non_orthogonality_gate", 70.0))
    if non_ortho is None:
        rows.append(("Max non-orthogonality", "not reported by the mesh check",
                     "", True))
    else:
        ok = float(non_ortho) <= gate
        rows.append(("Max non-orthogonality",
                     f"{float(non_ortho):.1f}° vs {gate:.0f}° gate",
                     "pass" if ok else "caveat", ok))
    skew = mesh.get("max_skewness")
    guidance = float(mesh.get("skewness_gate", 4.0))
    if skew is None:
        rows.append(("Max skewness", "not reported by the mesh check", "", True))
    else:
        ok = float(skew) <= guidance
        rows.append(("Max skewness",
                     f"{float(skew):.2f} vs {guidance:.1f} guidance",
                     "pass" if ok else "caveat", ok))
    return rows


def build_certificate_v2(report_doc: dict, *, out_path: str | Path,
                         geometry: str, objective: str, mission_id: str,
                         issued_utc: str, channels: Iterable[dict] | None = None,
                         display_name: str | None = None,
                         source_filename: str | None = None,
                         solver: str | None = None,
                         fidelity: str | None = None,
                         mesh: dict | None = None,
                         scope: str | None = None,
                         constraints: Iterable[Any] | None = None,
                         assumptions: Iterable[Any] | None = None
                         ) -> dict[str, Any]:
    """Redesigned certificate: a certificate, not a log dump.

    Serif/sans pairing, a human certificate number in the masthead (the mission
    slug is demoted to provenance metadata), a subject block leading with the
    geometry DISPLAY NAME, a result block with value +- 95% CI and a fidelity
    chip, the complete three-channel uncertainty table, and a provenance footer
    carrying the SHA-256 seal (truncated + full).

    ``mesh`` carries the mission's actual checkMesh facts for the solved-mesh
    acts (cells, max non-orthogonality, max skewness plus their gates); when
    given it is sealed with the run and rendered as a mesh-validity block with
    pass/caveat verdicts against the stated gates.

    ``report_doc["result_fields"]`` (ordered label/value pairs) renders the
    result block as a two-column Parameter | Value table — labels arrive in
    Title Case from the act, values verbatim — and is sealed with the run.
    Acts not yet migrated keep the sentence fallback.

    ``scope`` is a labelled field, not fine print: it states what was actually
    optimized and what the reported quantity covers, and it sits directly under
    the objective so the two are read together.

    ``constraints`` is the run's complete constraint list as (name, value,
    tag) rows, where the tag says whether a limit was stated by the user,
    assumed by the act, or raised as an advisory nobody asked for. An advisory
    row carries its disposition in the same tag column, so the page says what
    happened to it rather than only that it fired.

    ``assumptions`` is the assumed-values ledger as (quantity, value, basis)
    rows: every number the answer rests on that neither the request stated nor
    a solver produced. Both tables are sealed with the run, and both are
    optional, so an act that passes neither renders exactly as before.

    Additive and non-default: nothing here changes ``build_certificate``.
    """
    results = list(report_doc.get("results", []))
    if isinstance(channels, dict):
        channels = channels.get("channels", [])
    channels = [c for c in (channels or []) if isinstance(c, dict)]
    compute = report_doc.get("compute", {})
    result_fields = _normalized_result_fields(report_doc.get("result_fields"))
    constraint_rows = _normalized_triples(constraints)
    assumption_rows = _normalized_triples(assumptions)
    scope = str(scope).strip() if scope else None
    primary = results[0] if results else {}
    tier = (primary.get("tier") or "").upper()
    chip = (fidelity or _infer_fidelity(tier, compute, results)).upper()
    subject = display_name_for(geometry, display_name)

    seal = evidence_hash(_seal_payload(
        mission_id=mission_id, geometry=geometry, objective=objective,
        results=results, channels=channels, compute=compute,
        issued_utc=issued_utc, mesh=mesh, result_fields=result_fields,
        scope=scope, constraints=constraint_rows,
        assumptions=assumption_rows))
    cert_no = _human_number(mission_id, issued_utc, seal)

    left = _MARGIN + 8
    right = _PAGE_W - _MARGIN - 8
    width = right - left
    # The body must never run into the provenance box at the page bottom.
    page_floor = _MARGIN + 22 + 66 + 8

    def render(level: int, paginate: bool = False) -> tuple[_Canvas, float]:
        """Draw the body once at the given density; return (canvas, final y).

        Level 0 is the exact spacing the signed-off redesign shipped with;
        level 1 is the tightened rhythm the mesh-validity certificates already
        use; level 2 additionally compacts the note leading and table rows.
        A dense run tightens its rhythm rather than spilling over the
        provenance box — wording, numbers, and order never change between
        levels.

        ``paginate`` is the last resort, used only when even the densest
        rhythm cannot hold the body on one leaf: the constraint list and the
        ledger then continue onto a second page in the same order. Tightening
        is always tried first, so a certificate that fitted before still
        renders as a single page.
        """
        compact = level >= 1
        dense = level >= 2
        note_size = 8.0 if dense else 8.5
        note_lead = 9.0 if dense else (10.0 if compact else 11.0)
        row_lead = 11.5 if dense else (12.0 if compact else 13.0)
        field_lead = 11.5 if dense else (12.0 if compact else 14.0)

        def gap(normal: float, tight: float) -> float:
            return tight if compact else normal

        c = _Canvas()
        y = _PAGE_H - _MARGIN - 6

        def room(need: float, at: float) -> float:
            """Keep ``need`` points of body on this leaf, or start the next.

            Returns the y to carry on drawing at. With pagination off it is
            the identity, so the measured overflow still drives the fit loop.
            """
            if not paginate or at - need >= page_floor:
                return at
            c.new_page()
            top = _PAGE_H - _MARGIN - 6
            c.text(left, top - 12, "CERTONOMOUS", size=13, bold=True,
                   color=_INK, serif=True)
            c.text(right - 150, top - 12, f"Certificate No. {cert_no}",
                   size=8, bold=True, color=_MUTED)
            top -= 24
            c.rule(left, top, right, width=1.0, color=_INK)
            return top - gap(26, 22)

        # -- masthead: wordmark (serif) + document class + human number -----
        c.text(left, y - 18, "CERTONOMOUS", size=25, bold=True, color=_INK, serif=True)
        c.text(left, y - 33, "Certificate of Autonomous Solve", size=8.5, bold=True,
               color=_MUTED)
        c.text(right - 150, y - 6, "Certificate No.", size=8, bold=True, color=_MUTED)
        c.text(right - 150, y - 22, cert_no, size=15, bold=True, color=_INK, serif=True)
        y -= 48
        c.rule(left, y, right, width=1.4, color=_INK)
        y -= gap(30, 24)

        # -- subject block ---------------------------------------------------
        c.text(left, y, "Subject", size=8, bold=True, color=_MUTED)
        y -= gap(22, 20)
        for line in _wrap(subject, 19, width):
            c.text(left, y, line, size=19, bold=True, color=_INK, serif=True)
            y -= gap(23, 22)
        if source_filename:
            c.text(left, y, f"source geometry: {source_filename}", size=8.5,
                   color=_MUTED)
            y -= gap(16, 14)
        y -= gap(6, 4)
        # Objective first and verbatim, then what the run actually covered,
        # then what solved it. Scope sits between them because it qualifies
        # the objective and is read with it, never as a footnote.
        fields = [("Objective", objective)]
        if scope:
            fields.append(("Scope", scope))
        fields.append(("Solver & Model", solver or "-"))
        for label, value in fields:
            c.text(left, y, label, size=8, bold=True, color=_MUTED)
            for line in _wrap(str(value), 10.5, width - 120):
                c.text(left + 120, y, line, size=10.5, color=_INK)
                y -= gap(14, 13)
            y -= gap(6, 5)
        y -= gap(6, 4)
        c.rule(left, y, right)
        y -= gap(28, 22)

        # -- constraint list and assumed-values ledger -----------------------
        # Every limit the run applied, tagged by where it came from, and every
        # number the answer rests on that neither the request stated nor a
        # solver produced. They sit ahead of the result because they are what
        # the result is conditional on.
        for title, head, rows in (
                ("Constraints", ("Constraint", "Limit", "Basis"),
                 constraint_rows),
                ("Assumed Values", ("Quantity", "Value", "Basis"),
                 assumption_rows)):
            if not rows:
                continue
            y = room(38 + row_lead * min(len(rows), 3), y)
            c.text(left, y, title, size=8, bold=True, color=_MUTED)
            y -= gap(8, 6)
            c.rule(left, y, right, width=0.5)
            y -= gap(16, 14)
            for i, cell in enumerate(head):
                c.text(left + (0, 150, 290)[i], y, cell, size=7.5, bold=True,
                       color=_MUTED)
            y -= gap(6, 5)
            c.rule(left, y, right, width=0.5)
            y -= gap(16, 14)
            for name, value, tag in rows:
                y = room(row_lead, y)
                c.text(left, y, name, size=9.5, bold=True, color=_INK)
                c.text(left + 150, y, value, size=9.5, color=_INK)
                if tag:
                    c.text(left + 290, y, tag, size=9, color=_MUTED)
                y -= row_lead
            y -= gap(12, 8)
            c.rule(left, y, right)
            y -= gap(26, 20)

        # -- result block: value +- CI + fidelity chip -----------------------
        # The headline, its chip and its caption are one unit and never split
        # across a leaf.
        y = room(96, y)
        c.text(left, y, "Result", size=8, bold=True, color=_MUTED)
        # SOLVER-BACKED is the unlabeled default for this simulation platform:
        # a real solve with no further chip renders no badge at all.
        shown_chip = _resolved_tier(chip)
        if shown_chip and shown_chip != "SOLVER-BACKED":
            chip_color = _FIDELITY_COLOR.get(shown_chip, _DEFAULT_FIDELITY_COLOR)
            chip_w = max(96.0, len(shown_chip) * 6.4 + 22)
            c.rect(right - chip_w, y - 5, chip_w, 21, fill=chip_color)
            c.text(right - chip_w + 11, y + 1, shown_chip, size=9.5, bold=True, color=_WHITE)
        y -= gap(30, 26)
        quantity = str(primary.get("quantity", "Result"))
        value = str(primary.get("value", ""))
        env = primary.get("envelope")
        c.text(left, y, quantity, size=11, color=_MUTED)
        y -= gap(26, 24)
        # Some report envelopes already carry their own leading "±"; never
        # print the sign twice.
        env_text = env.lstrip("± ").strip() if env else ""
        # The envelope field is not always an interval. Acts legitimately put
        # a gate threshold, a convergence iteration, a mesh reading or a
        # reference condition here: "converged at iteration 1,734",
        # "5% pass threshold", "non-orthogonality 40.5 vs 70 gate". Printing
        # "95% confidence interval" under those is not a formatting slip, it
        # states a statistical claim the run never made, on a sealed
        # certificate. Only an interval is labelled as one; everything else
        # prints as itself, and a bare value stays a point estimate.
        is_interval = bool(env_text) and _looks_like_interval(env_text)
        if is_interval:
            headline = f"{value}   {_fold('±')} {env_text}"
            caption = "95% confidence interval"
        elif env_text:
            headline = value
            caption = env_text
        else:
            headline = value
            caption = "point estimate"
        c.text(left, y, headline, size=24, bold=True, color=_INK, serif=True)
        c.text(left + 8, y - 16, caption, size=8.5, color=_MUTED)
        y -= gap(34, 30)
        reason = primary.get("reason")
        if reason:
            for line in _wrap(reason[:1].upper() + reason[1:], 9.5, width):
                c.text(left, y, line, size=9.5, color=_MUTED)
                y -= gap(13, 12)
        # Shared column grid for the result, channel, and mesh tables: label
        # at the left edge, values at +150, state/verdict at +290.
        val_x, state_x = 150, 290
        if result_fields:
            # Structured result: a clean Parameter | Value table, labels in
            # Title Case from the act, every value verbatim. It replaces the
            # secondary prose lines for the acts that carry it.
            y -= gap(4, 2)
            c.rule(left, y, right, width=0.5)
            y -= gap(15, 13)
            c.text(left, y, "Parameter", size=7.5, bold=True, color=_MUTED)
            c.text(left + val_x, y, "Value", size=7.5, bold=True, color=_MUTED)
            y -= gap(6, 5)
            c.rule(left, y, right, width=0.5)
            y -= gap(15, 13)
            for label, value in result_fields:
                c.text(left, y, label, size=9.5, bold=True, color=_INK)
                c.text(left + val_x, y, value, size=9.5, color=_INK)
                y -= field_lead
        else:
            # secondary results; a "Mesh" line is skipped when the dedicated
            # mesh-validity block below carries those facts with verdicts.
            for item in results[1:]:
                if mesh and str(item.get("quantity", "")).strip().lower() == "mesh":
                    continue
                c.text(left, y, str(item.get("quantity", "")), size=9, bold=True, color=_INK)
                val = str(item.get("value", ""))
                ienv = item.get("envelope")
                c.text(left + 160, y, f"{val}   {ienv}" if ienv else val, size=9, color=_MUTED)
                y -= gap(13, 12)
        y -= gap(10, 6)
        c.rule(left, y, right)
        y -= gap(26, 20)

        # -- three-channel uncertainty table ---------------------------------
        y = room(54 + row_lead, y)
        c.text(left, y, "Uncertainty", size=8, bold=True, color=_MUTED)
        y -= gap(8, 6)
        c.rule(left, y, right, width=0.5)
        y -= gap(16, 14)
        c.text(left, y, "Channel", size=7.5, bold=True, color=_MUTED)
        c.text(left + val_x, y, "Value", size=7.5, bold=True, color=_MUTED)
        c.text(left + state_x, y, "State", size=7.5, bold=True, color=_MUTED)
        y -= gap(6, 5)
        c.rule(left, y, right, width=0.5)
        y -= gap(16, 14)
        table = channels or [{"name": n} for n in ("Input", "Numerical", "Model form")]
        for ch in table:
            name, cval, quantified, note = _channel_fields(ch)
            y = room(row_lead + (note_lead * 2 if note else 0), y)
            state = "quantified" if quantified else "not quantified"
            c.text(left, y, name, size=9.5, bold=True, color=_INK)
            c.text(left + val_x, y, cval, size=9.5, color=_INK)
            c.text(left + state_x, y, state, size=9,
                   color=_MUTED if quantified else (0.66, 0.45, 0.10))
            y -= row_lead
            if note:
                # One line per sentence/bullet of the note, first letter
                # capitalized; long sentences still wrap in their own block.
                for sentence in _note_lines(note):
                    for line in _wrap(sentence, note_size, width - 14):
                        c.text(left + 14, y, line, size=note_size, color=_MUTED)
                        y -= note_lead
            y -= gap(4, 3)

        # -- mesh validity (solved-mesh acts) --------------------------------
        if mesh:
            rows = _mesh_rows(mesh)
            # Tighten the row rhythm when the remaining room is short rather
            # than stranding rows against the footer.
            row_h = 13.0 if y - (21 + 13.0 * len(rows)) >= page_floor + 4 else 11.0
            y -= 4
            c.rule(left, y + 12, right, width=0.5)
            c.text(left, y - 2, "Mesh Validity", size=8, bold=True, color=_MUTED)
            y -= 17
            for name, measured, verdict, ok in rows:
                c.text(left, y, name, size=9.5, bold=True, color=_INK)
                c.text(left + val_x, y, measured, size=9.5, color=_INK)
                if verdict:
                    c.text(left + state_x, y, verdict, size=9,
                           color=_MUTED if ok else (0.66, 0.45, 0.10))
                y -= row_h
            y -= 4
        return c, y

    # Fit loop: start at the density this certificate class ships with and
    # tighten only when the body would otherwise reach the provenance box. A
    # body that still will not fit at the tightest rhythm continues onto a
    # second leaf rather than being cut, so nothing the run applied is
    # dropped for want of room.
    density = 1 if mesh else 0
    c, body_bottom = render(density)
    while body_bottom < page_floor and density < 2:
        density += 1
        c, body_bottom = render(density)
    if body_bottom < page_floor:
        c, body_bottom = render(2, paginate=True)

    # -- provenance footer -------------------------------------------------
    # Issuance and the seal that covers it sit together at the foot of the
    # last leaf: when the certificate was issued, and the hash that proves
    # what it said when it was.
    foot_h = 66
    fy = _MARGIN + 22
    c.rect(left, fy, width, foot_h, fill=(0.965, 0.972, 0.980))
    ty = fy + foot_h - 15
    c.text(left + 12, ty, "Issued (UTC)", size=8, bold=True, color=_SEAL)
    c.text(left + 92, ty, issued_utc, size=8.5, color=_INK)
    c.text(right - 190, ty, "Evidence Seal  ·  SHA-256", size=8,
           bold=True, color=_SEAL)
    ty -= 15
    c.text(left + 12, ty, seal[:32], size=9, bold=True, color=_SEAL)
    c.text(left + 12, ty - 11, seal[32:], size=9, bold=True, color=_SEAL)
    ty -= 24
    c.text(left + 12, ty, f"Mission {mission_id}   ·   Certificate {cert_no}",
           size=8, color=_MUTED)

    out_path = _write_pdf_atomic(out_path, c.to_pdf())
    return {"path": str(out_path), "hash": seal, "mission_id": mission_id,
            "tier": tier, "fidelity": chip, "certificate_no": cert_no}
