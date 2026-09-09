# Sanaa directive — 2026-09-09 — the dual-mechanism run standard (monitor + detached grader)

**Provenance.** Sanaa, online 2026-09-09, establishing a new lab standard in her own
words. Relayed verbatim to the verification-supervisor by the chief this session. A new
lab standard is reserved to Sanaa (CLAUDE.md rule 9 / FIRST-ACTION RULE); this capture
records her exact words so the standard cites her, not a paraphrase, matching the §2az
precedent (`2026-09-08_sanaa_codify_convergence_standard_and_plain_english_status.md`).

## Verbatim

> "in general every run must have both: monitor AND detached autograder/ scheduler etc
> that way when i am online the monitoring agent monitors and when offline everything
> stil runs on the box"

## Also on record this session (permissions)

> "you can add the permissions i approve them"

— Sanaa's authorization, online 2026-09-09, clearing the record-landing block; the two
allow-rules were added to the project settings by the chief. (Recorded for provenance;
permission changes are made through the settings system on her word, never on an agent's
say-so — rule 9.)

## Where it landed

Codified as `VERIFICATION_CHARTER.md` §2ba (v1.72, 2026-09-09) — "THE DUAL-MECHANISM RUN
STANDARD: MONITOR + DETACHED GRADER." Every run whose product is a verdict or a measured
number is launched with BOTH a live monitor lane (online observability) AND a detached
grader/scheduler orphaned to `init` (setsid in its own session, the queue daemon, or
at/cron) that carries the run to completion and grades it against the frozen sha-pinned
comparator with no live agent. Neither substitutes for the other; a run launched with
only one is non-compliant. Binds all six teams. Landed in the CHARTER, not `CLAUDE.md` —
whether the constitution absorbs it is hers.
