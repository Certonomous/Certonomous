"""Claude-backed narration voice for the mission transcript.

Every transcript line can be rephrased by Claude so the on-camera narration
reads like a working engineer instead of a format string.  The layer is
strictly cosmetic and strictly optional:

- Off unless CERTONOMOUS_VOICE is set (tests and CI never touch the network).
- Every number, unit, and symbol in the original line must survive the
  rewrite verbatim; otherwise the original line is used.  Claude can change
  the phrasing, never the physics.
- Any failure (no key, timeout, refusal) falls back to the original line.
- Rewrites are cached on disk keyed by the exact input, so a rehearsal run
  pays the latency once and the live demo replays from cache, even offline.

Configuration (environment):
    CERTONOMOUS_VOICE          enable when set to anything truthy
    ANTHROPIC_API_KEY          credentials for the Claude API
    CERTONOMOUS_VOICE_MODEL    model id, default claude-opus-4-8
    CERTONOMOUS_VOICE_TIMEOUT  per-call timeout in seconds, default 10
    CERTONOMOUS_VOICE_CACHE    cache directory override
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

DEFAULT_MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = (
    "You are the narration voice of Certonomous, an autonomous aerodynamics "
    "laboratory, speaking on the record during a live mission. You receive one "
    "line of the mission transcript, prefixed by the role that speaks it. "
    "Rewrite the line so it reads like a capable working engineer narrating "
    "naturally, not a template.\n"
    "Hard rules:\n"
    "- Preserve every number, unit, symbol, and technical term exactly as "
    "written. Do not round, convert, drop, or add any quantity.\n"
    "- State only what the line states. Never add claims, causes, or results.\n"
    "- Keep it to one line of similar length. No preamble, no quotes, no "
    "markdown, no em dashes (use commas).\n"
    "- Keep the register calm, precise, and first-person-plural where natural.\n"
    "Reply with the rewritten line only."
)

_NUMBER = re.compile(r"[-+]?\d+(?:[.,]\d+)*(?:[eE][-+]?\d+)?")

_client = None  # lazily constructed, reused across calls


def enabled() -> bool:
    return bool(os.environ.get("CERTONOMOUS_VOICE"))


def _cache_dir() -> Path:
    override = os.environ.get("CERTONOMOUS_VOICE_CACHE")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2] / "mission-output" / ".voice-cache"


def _cache_path(model: str, role: str, message: str) -> Path:
    key = hashlib.sha256(f"{model}\n{role}\n{message}".encode("utf-8")).hexdigest()
    return _cache_dir() / f"{key}.txt"


def _numbers_survive(original: str, rewritten: str) -> bool:
    """Every numeric token of the original must appear verbatim in the rewrite."""
    return all(token in rewritten for token in _NUMBER.findall(original))


def _complete(role: str, message: str, model: str) -> str:
    """One Claude call. Isolated so tests can stub it. Raises on any failure."""
    global _client
    if _client is None:
        import anthropic

        timeout = float(os.environ.get("CERTONOMOUS_VOICE_TIMEOUT", "10"))
        # Fail fast: a slow call must never stall the mission, the fallback
        # is the perfectly serviceable scripted line.
        _client = anthropic.Anthropic(timeout=timeout, max_retries=0)
    response = _client.messages.create(
        model=model,
        max_tokens=300,
        output_config={"effort": "low"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"{role}: {message}"}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("voice request refused")
    text = next(b.text for b in response.content if b.type == "text")
    return text.strip().strip('"')


def polish(role: str, message: str) -> str:
    """Return the Claude-voiced line, or the original on any doubt."""
    if not enabled() or not message.strip():
        return message
    model = os.environ.get("CERTONOMOUS_VOICE_MODEL", DEFAULT_MODEL)
    cache = _cache_path(model, role, message)
    if cache.exists():
        cached = cache.read_text(encoding="utf-8")
        return cached if cached.strip() else message
    try:
        rewritten = _complete(role, message, model)
    except Exception:
        return message
    rewritten = rewritten.replace("—", ",").replace("\n", " ").strip()
    if not rewritten or not _numbers_survive(message, rewritten):
        return message
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(rewritten, encoding="utf-8")
    except OSError:
        pass
    return rewritten
