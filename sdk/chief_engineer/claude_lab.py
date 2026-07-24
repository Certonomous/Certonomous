"""The lab's shared Claude client: one hardened door to the model.

Every part of the team that wants Claude's help — the mission debrief, the
ask-the-lab reasoning layer, future callers — goes through :func:`complete`.
The hardening mirrors ``voice.py``: a lazily built client reused across calls,
a short per-call timeout, no retries, and a silent ``None`` on any failure, so
a Claude outage can never break a mission or a page. Callers must always have
a deterministic fallback ready; ``None`` means "the model had nothing safe to
add", never an error to surface.

Claude writes prose only. Nothing that comes back through this module may be
treated as a measurement — numeric results are produced by solvers and guarded
by the callers, not by the model.

Configuration (environment):
    ANTHROPIC_API_KEY           credentials; absent means the whole layer is off
    CERTONOMOUS_CLAUDE          set to 0 to disable even when a key is present
    CERTONOMOUS_CLAUDE_MODEL    model id, default claude-opus-4-8
    CERTONOMOUS_CLAUDE_TIMEOUT  per-call timeout in seconds, default 15
"""

from __future__ import annotations

import os

DEFAULT_MODEL = "claude-opus-4-8"

_client = None  # lazily constructed, reused across calls


def enabled() -> bool:
    """True when the lab may talk to Claude at all."""
    if os.environ.get("CERTONOMOUS_CLAUDE", "").strip() == "0":
        return False
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _model() -> str:
    return os.environ.get("CERTONOMOUS_CLAUDE_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _get_client():
    global _client
    if _client is None:
        import anthropic

        timeout = float(os.environ.get("CERTONOMOUS_CLAUDE_TIMEOUT", "15"))
        # Fail fast and never retry: the deterministic path is always there,
        # and a slow model call must never stall a mission or a page.
        _client = anthropic.Anthropic(timeout=timeout, max_retries=0)
    return _client


def complete(system: str, user: str, *, max_tokens: int = 700,
             effort: str = "low") -> str | None:
    """One Claude call, or None on any doubt.

    Returns the model's text reply, stripped, or ``None`` when the layer is
    disabled, the input is empty, the model refuses, or anything at all fails.
    ``effort`` is kept low or medium for latency; adaptive thinking lets the
    model decide how much deliberation the prompt deserves.
    """
    if not enabled() or not (user or "").strip():
        return None
    try:
        response = _get_client().messages.create(
            model=_model(),
            max_tokens=max_tokens,
            thinking={"type": "adaptive"},
            output_config={"effort": effort},
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        if response.stop_reason == "refusal":
            return None
        text = "".join(
            block.text for block in response.content
            if getattr(block, "type", None) == "text").strip()
        return text or None
    except Exception:
        return None
