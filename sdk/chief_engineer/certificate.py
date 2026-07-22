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
controller.  Text is emitted in WinAnsi so ``±``, ``°``, ``×`` and the em dash
render; a few maths glyphs that WinAnsi lacks are folded to ASCII first.
"""

from __future__ import annotations

import hashlib
import json
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
    "TREND ONLY": (0.80, 0.53, 0.11),
    "NEEDS WORK": (0.72, 0.20, 0.20),
}
_DEFAULT_TIER_COLOR = (0.42, 0.46, 0.51)

# WinAnsi cannot encode these; fold to something it can before laying out text.
_GLYPH_FOLD = {
    "≈": "~", "≥": ">=", "≤": "<=", "−": "-",
    "–": "-", "‑": "-", "→": "->",
    "“": '"', "”": '"', "‘": "'", "’": "'",
    "·": "-",
}


# --------------------------------------------------------------------------
# Minimal PDF canvas
# --------------------------------------------------------------------------

class _Canvas:
    """Accumulate drawing operators for one page, then serialise to PDF bytes."""

    def __init__(self) -> None:
        self._ops: list[str] = []

    # -- primitives --------------------------------------------------------
    def text(self, x: float, y: float, s: str, size: float = 10.0,
             bold: bool = False, color=_INK) -> None:
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
        content = "\n".join(self._ops).encode("cp1252", "replace")
        objects: list[bytes] = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {_PAGE_W:.2f} "
             f"{_PAGE_H:.2f}] /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> "
             f"/Contents 4 0 R >>").encode("ascii"),
            (b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n"
             + content + b"\nendstream"),
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
            b"/Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
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
    return s


def _escape(s: str) -> str:
    s = _fold(s)
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _avg_width(size: float) -> float:
    # Helvetica averages ~0.52 em across running text; enough for wrapping.
    return 0.52 * size


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
                  compute, issued_utc) -> dict:
    """The exact fields the seal covers — nothing cosmetic, everything factual."""
    return {
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
    c.text(right - 180, y - 12, "CERTIFICATE OF AUTONOMOUS SOLVE",
           size=8.5, bold=True, color=_MUTED)
    c.text(right - 180, y - 24, f"Mission {mission_id}", size=8.5, color=_MUTED)
    y -= 34
    c.rule(left, y, right, width=1.1, color=_INK)
    y -= 26

    # -- identity fields ---------------------------------------------------
    for label, value in (("Geometry", geometry), ("Objective", objective),
                         ("Issued (UTC)", issued_utc)):
        c.text(left, y, label.upper(), size=8, bold=True, color=_MUTED)
        for line in _wrap(value, 11, width - 96):
            c.text(left + 96, y, line, size=11, color=_INK)
            y -= 15
        y -= 5
    y -= 8

    # -- headline result + trust badge ------------------------------------
    if primary:
        c.text(left, y, "RESULT", size=8, bold=True, color=_MUTED)
        y -= 20
        headline = f"{primary.get('quantity', 'Result')}   {primary.get('value', '')}"
        c.text(left, y, headline, size=17, bold=True, color=_INK)
        badge = _TIER_COLOR.get(tier, _DEFAULT_TIER_COLOR)
        badge_w = max(78.0, len(tier) * 6.6 + 20)
        c.rect(right - badge_w, y - 4, badge_w, 20, fill=badge)
        c.text(right - badge_w + 10, y + 1.5, tier or "UNRATED",
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
    c.text(left, y, "UNCERTAINTY CHANNELS  ·  ASME V&V 20", size=8, bold=True,
           color=_MUTED)
    y -= 18
    if channels:
        for ch in channels:
            state = "quantified" if ch.get("quantified") else "not quantified"
            name = str(ch.get("name", ""))
            value = str(ch.get("value", "")) if ch.get("value") is not None else "-"
            c.text(left, y, name, size=9.5, bold=True, color=_INK)
            c.text(left + 130, y, value, size=9.5, color=_INK)
            c.text(left + 230, y, f"({state})", size=9,
                   color=_MUTED if ch.get("quantified") else _DEFAULT_TIER_COLOR)
            y -= 13
            note = ch.get("note")
            if note:
                for line in _wrap(note, 8.5, width - 12):
                    c.text(left + 12, y, line, size=8.5, color=_MUTED)
                    y -= 11
            y -= 4
    else:
        for line_txt in report_doc.get("uncertainty", [])[:3]:
            for line in _wrap(line_txt, 9, width):
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
        c.text(left, y, "COMPUTE", size=8, bold=True, color=_MUTED)
        c.text(left + 96, y, "   ·   ".join(compute_bits), size=9.5, color=_INK)
        y -= 20

    # -- evidence seal -----------------------------------------------------
    seal_h = 58
    c.rect(left, _MARGIN + 30, width, seal_h, fill=(0.96, 0.97, 0.98))
    sy = _MARGIN + 30 + seal_h - 16
    c.text(left + 12, sy, "EVIDENCE-BUNDLE SEAL  ·  SHA-256", size=8, bold=True,
           color=_SEAL)
    sy -= 16
    c.text(left + 12, sy, seal[:32], size=9.5, bold=True, color=_SEAL)
    c.text(left + 12, sy - 12, seal[32:], size=9.5, bold=True, color=_SEAL)

    # -- footer ------------------------------------------------------------
    c.text(left, _MARGIN + 12,
           "Sealed by the hash above; any change to the recorded run invalidates it. "
           "No tier exceeds TREND ONLY without an experimental comparison.",
           size=7.5, color=_MUTED)

    out_path = Path(out_path).with_suffix(".pdf")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(c.to_pdf())
    return {"path": str(out_path), "hash": seal, "mission_id": mission_id,
            "tier": tier}
