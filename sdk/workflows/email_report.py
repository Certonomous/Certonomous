"""Closing beat — email the mission report as a table.

Configure once (never commit these; use an app password):

    setx CERTONOMOUS_SMTP_HOST smtp.gmail.com
    setx CERTONOMOUS_SMTP_PORT 587
    setx CERTONOMOUS_SMTP_USER you@gmail.com
    setx CERTONOMOUS_SMTP_PASSWORD <app-password>
    setx CERTONOMOUS_SMTP_TO you@mit.edu

Then:

    python -m workflows.email_report                     # emails the latest mission
    python -m workflows.email_report --check             # config check, sends nothing
    python -m workflows.email_report uncertainty-reduction # a specific workflow
"""

from __future__ import annotations

import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

from . import OUT_ROOT

REQUIRED = ("CERTONOMOUS_SMTP_HOST", "CERTONOMOUS_SMTP_TO")


def _latest_mission() -> Path | None:
    candidates = [p for p in OUT_ROOT.iterdir() if p.is_dir()] if OUT_ROOT.exists() else []
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def _html_table(rows: list[tuple[str, str]], title: str) -> str:
    body = "".join(
        f"<tr><td style='padding:6px 12px;border-bottom:1px solid #e3e7ec;"
        f"color:#6b7684;white-space:nowrap'>{key}</td>"
        f"<td style='padding:6px 12px;border-bottom:1px solid #e3e7ec;"
        f"color:#1c2430'><b>{value}</b></td></tr>"
        for key, value in rows)
    return (
        f"<div style='font-family:-apple-system,Segoe UI,sans-serif'>"
        f"<h2 style='color:#1c2430;margin-bottom:4px'>Certonomous — {title}</h2>"
        f"<p style='color:#6b7684;margin-top:0;font-size:13px'>"
        f"Every value below came from a real OpenFOAM solve on the mission "
        f"compute node.</p>"
        f"<table style='border-collapse:collapse;font-size:14px'>{body}</table></div>")


def _rows_from_transcript(transcript: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line or line.startswith("==="):
            continue
        role, _, message = line.partition(":")
        if role.strip() in {"CHIEF ENGINEER", "CHIEF RESEARCHER"} and any(
                token in message for token in ("=", "±", "VERDICT", "Winner", "APPROVED", "REJECTED")):
            rows.append((role.strip().title(), message.strip()[:400]))
    return rows[-12:]


def main(workflow: str | None = None, check_only: bool = False) -> int:
    missing = [name for name in REQUIRED if not os.environ.get(name)]
    if check_only or missing:
        status = "READY" if not missing else f"NOT CONFIGURED (missing: {', '.join(missing)})"
        print(f"SMTP {status}")
        print(f"  host={os.environ.get('CERTONOMOUS_SMTP_HOST', '—')} "
              f"port={os.environ.get('CERTONOMOUS_SMTP_PORT', '587')} "
              f"user={os.environ.get('CERTONOMOUS_SMTP_USER', '—')} "
              f"to={os.environ.get('CERTONOMOUS_SMTP_TO', '—')}")
        return 0 if not missing else 1

    directory = (OUT_ROOT / workflow) if workflow else _latest_mission()
    if directory is None or not directory.exists():
        print(f"No mission output found in {OUT_ROOT}")
        return 1
    transcript = directory / "transcript.txt"
    if not transcript.exists():
        print(f"No transcript in {directory}")
        return 1

    rows = _rows_from_transcript(transcript)
    message = EmailMessage()
    message["Subject"] = f"Certonomous report — {directory.name}"
    message["From"] = os.environ.get("CERTONOMOUS_SMTP_USER", "certonomous@localhost")
    message["To"] = os.environ["CERTONOMOUS_SMTP_TO"]
    message.set_content(transcript.read_text(encoding="utf-8", errors="replace"))
    message.add_alternative(_html_table(rows, directory.name), subtype="html")

    for png in sorted(directory.glob("*.png")):
        message.add_attachment(png.read_bytes(), maintype="image",
                               subtype="png", filename=png.name)
    for pdf in sorted(directory.glob("*.pdf")):
        message.add_attachment(pdf.read_bytes(), maintype="application",
                               subtype="pdf", filename=pdf.name)

    host = os.environ["CERTONOMOUS_SMTP_HOST"]
    port = int(os.environ.get("CERTONOMOUS_SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=45) as smtp:
        smtp.starttls()
        user = os.environ.get("CERTONOMOUS_SMTP_USER")
        if user:
            smtp.login(user, os.environ.get("CERTONOMOUS_SMTP_PASSWORD", ""))
        smtp.send_message(message)
    plots = len(list(directory.glob("*.png")))
    certs = len(list(directory.glob("*.pdf")))
    print(f"Report for {directory.name} emailed to {message['To']} "
          f"({len(rows)} rows, {plots} plot(s), {certs} certificate(s) attached).")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    raise SystemExit(main(args[0] if args else None, "--check" in sys.argv))
