# Blocked items — consolidated waiting-on-Sanaa list

Single source of truth for work that cannot proceed on this box. Everything
here has been **verified blocked**, not assumed. Nothing else in the night queue
waits on an answer; each entry names the exact unblock action.

Kept as a separate file on purpose: `agenda.save_docket()` rewrites
`docket.json`'s proposal list wholesale, so a blocker parked as a top-level key
there would be silently destroyed by the next `refresh_docket()`.

Last updated: 2026-07-28 00:0x UTC.

---

## B-1. Billing alarm and spend cap cannot be confirmed from this instance

**Ops gate item 1. BLOCKED — verification, not assumption.**

| Check | Result |
| --- | --- |
| IAM instance role | **None.** `/latest/meta-data/iam/security-credentials/` returns 404 |
| `~/.aws` | Does not exist |
| `AWS_*` environment variables | None set |
| `aws` CLI | Not installed |

With no credentials and no role, this box cannot call CloudWatch or Billing,
so **I cannot report the configured alarm threshold or spend cap.** Installing
the CLI would not help; the credentials are the missing piece, not the tool.

**I am explicitly NOT reporting a number here.** Stating an unverified spend cap
would be exactly the kind of fabricated measurement the house rules forbid.

**Unblock:** attach an instance role with `cloudwatch:DescribeAlarms` and
`ce:GetCostAndUsage` (read-only is sufficient), or paste the configured numbers
directly and they will be recorded as reported-by-owner rather than measured.

---

## B-2. Ledger cannot be synced off-host

**Ops gate item 3. BLOCKED both paths.**

| Path | Status |
| --- | --- |
| S3 | No credentials, no role, no CLI — same as B-1 |
| Private GitHub remote | `origin` **is** configured (`https://github.com/Certonomous/Certonomous.git`) but there is no usable credential: `~/.ssh` holds only `authorized_keys` (no private key), and `ssh -T git@github.com` returns `Permission denied (publickey)`. No HTTPS token or credential helper is configured. |

**Current state and the honest risk.** A verified local backup exists at
`/home/ubuntu/backups/ledger_20260727_235551.jsonl` (89,964,387 bytes, MD5
`7b2e586edb384528b44f3df81ae2651e`, 192,409 lines). **It is on the same disk as
the ledger it backs up.** That protects against corruption, a bad
de-duplication, and accidental deletion. It does **not** protect against losing
the instance — which is precisely what happened on 2026-07-27. The disk
surviving that outage was luck, not design.

The single-instance lock stays in force (`acquire_runner_lock`, commit
`f198cf4`), which is the other half of ledger integrity and is **not** blocked.

**Unblock:** either an instance role with `s3:PutObject` on a backup bucket, or
a deploy key / PAT for the private repo. The moment either exists, the hourly
sync goes in — the backup script and rotation already work.

---

## B-3. TMR NACA 0012 closure run — approval ambiguity, NOT a technical block

Ladder C4 schedules the ~480 core-minute TMR closure run "within cap". Two
things are unresolved, and they are different:

1. **The cap itself is unknown** — see B-1. "Within cap" cannot be evaluated
   against a number nobody on this box can read.
2. The owner said "I am fine with the closure challenge cost" in response to a
   message that quoted **only** the TMR figure (~480 core-min / ~8 h) while also
   naming the separate closure-challenge track. The literal phrase matches the
   closure-challenge track, which needs no approval and is running.

**Handling:** the closure-challenge track (Ladder C1–C3) proceeds — it was never
gated. The 480 core-minute TMR run is scheduled per C4 but will be launched only
against a known cap or an explicit go, because launching an 8-hour compute
commitment on a misread of one ambiguous sentence is not a defensible default.

**Unblock:** confirm the spend cap (B-1), or say "yes, run the 480 core-min TMR
closure".
