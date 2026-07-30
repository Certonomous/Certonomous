"""Ask the lab a question from the terminal — the record-grounded answerer.

Prints whether the answer was grounded, whether it was a plain record listing or
reasoned over the record by the model (when ``ANTHROPIC_API_KEY`` is set), the
answer itself, and its citations. Nothing is executed; this only reads what the
lab has already recorded.

    python -m chief_engineer.ask_cli "what have we validated?"
    python -m chief_engineer.ask_cli "compare the flat plate and the naca4412"
    python -m chief_engineer.ask_cli --both "should I trust the ahmed_35 number?"

``--both`` runs the question twice — once forced deterministic and once with the
model — so you can see exactly what the reasoning layer adds. It needs the key.
"""

from __future__ import annotations

import os
import sys

from . import ask_the_lab


def _render(question: str, answer) -> str:
    head = ("GROUNDED" if answer.grounded else "NOT GROUNDED")
    mode = "reasoned from the record" if answer.mode == "synthesized" else "from the record"
    lines = [f"Q: {question}",
             f"[{head} · {mode}]",
             "",
             answer.text]
    if answer.citations:
        lines.append("")
        lines.append("Grounded in:")
        for citation in answer.citations:
            lines.append(f"  - {citation}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    both = False
    if "--both" in argv:
        both = True
        argv.remove("--both")
    question = " ".join(argv).strip() or sys.stdin.read().strip()
    if not question:
        print('Usage: python -m chief_engineer.ask_cli [--both] "<question>"',
              file=sys.stderr)
        return 2

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    if both:
        prior = os.environ.get("CERTONOMOUS_ASK_LLM")
        os.environ["CERTONOMOUS_ASK_LLM"] = "0"
        print("=== DETERMINISTIC (record listing) ===")
        print(_render(question, ask_the_lab.answer(question)))
        if prior is None:
            os.environ.pop("CERTONOMOUS_ASK_LLM", None)
        else:
            os.environ["CERTONOMOUS_ASK_LLM"] = prior
        print()
        print("=== WITH THE MODEL (reasoned over the same facts) ===")
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("(no ANTHROPIC_API_KEY in this shell, this half needs the key)")
        print(_render(question, ask_the_lab.answer(question)))
        return 0

    print(_render(question, ask_the_lab.answer(question)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
