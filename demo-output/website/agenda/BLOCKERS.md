# Blocked items — consolidated waiting-on-Sanaa list

Single source of truth for work that cannot proceed on this box. Everything
here has been **verified blocked**, not assumed. Nothing else in the night queue
waits on an answer; each entry names the exact unblock action.

Kept as a separate file on purpose: `agenda.save_docket()` rewrites
`docket.json`'s proposal list wholesale, so a blocker parked as a top-level key
there would be silently destroyed by the next `refresh_docket()`.

Last updated: 2026-08-01 06:3x UTC.

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

---

## B-4. External reachability cannot be settled from this box

**`w7-verify-reachability-from-outside`. BLOCKED on the half that matters.
Measured 2026-08-01 06:3x UTC.**

The gate asks readiness to name which surfaces are reachable from outside and
which are loopback only, **and to say how it knows**. Two different questions
hide in that sentence, and only one of them can be answered here.

**Answerable here, and now answered: the bind address.** `ss -ltnp` on this
instance:

| Port | Bind | Process |
| --- | --- | --- |
| 8080 | `0.0.0.0` | `python3 -m http.server 8080 --directory demo-output/website` (pid 1396) |
| 8765 | `0.0.0.0` | `python3 -m chief_engineer.server` (pid 2872620) |
| 22 | `0.0.0.0` and `[::]` | sshd |
| 53 | `127.0.0.53`, `127.0.0.54` | systemd-resolved |
| 35257 | `127.0.0.1` | ephemeral |

**Neither demo surface is loopback only.** That is a fact about this box and a
readiness check can assert it without leaving the instance. It is also not the
claim the shoot needed.

**Not answerable here: whether an outside client can open the socket.**

| Probe | Result |
| --- | --- |
| `http://127.0.0.1:8080/` | **200** |
| `http://172.31.43.247:8080/` (private address) | **200** |
| `http://16.58.201.228:8080/` (public address, from this box) | **000** |

The 000 is the trap, and it is worth naming precisely: **it is not evidence
that the port is closed.** An EC2 instance reaching its own elastic address
normally has no hairpin path back to itself, so 000 is the expected answer
whether the security group admits the world or blocks it. The check that looks
most like an outside test is the one check that can never distinguish the two
cases. It is a false negative by construction, in the same way the old
loopback test was a false positive by construction.

The security group is `launch-wizard-2`. Its inbound rules would settle the
question, and they cannot be read from here: there is no instance role
(`/latest/meta-data/iam/security-credentials/` returns 404), no `~/.aws`, no
`AWS_*` variables and no `aws` CLI, exactly as recorded in B-1.

**What readiness may claim today, and it should claim only this:** the bind
address of every listening socket, and a plain statement that reachability
from outside is unverified and cannot be verified from the instance.

**Unblock, cheapest first.**

1. From the operator laptop, off any Certonomous network:
   `curl -sS -o /dev/null -w '%{http_code}\n' --max-time 8 http://16.58.201.228:8080/`
   and the same for `:8765`. Two lines of output settle it permanently, and a
   200 or a 000 both go on the record with the vantage point named.
2. Or attach a read-only instance role with `ec2:DescribeSecurityGroups`, which
   turns this into a check the box can run for itself every week.

Until one of those exists, any readiness line that asserts external
reachability is asserting something nobody measured.

---

## B-5. Five papers this box cannot open, and one it can

**`w2-mit-access-list`, `w5-close-the-secco-2021-citation-gap`. Opened
2026-08-01. Waiting on Katie's library, not on this box.**

The full list, with what each item unblocks and the one section needed, is
`demo-output/website/agenda/LIBRARY_ACCESS_LIST.md`. It is ordered by
consequence and it is short enough to work in one sitting.

The first entry is the only one that can overturn something already published:
**Secco, Kenway, He, Mader and Martins, AIAA J. 59(4) 1151 to 1168, 2021, doi
10.2514/1.J059491**, which returned 403 on every URL tried and has no
open-access copy. The lab's root-cause document states that nothing qualifies
`warpDeriv` as approximate, and an undocumented defect and a documented
approximation are different things to report upstream. One paragraph of that
paper either upholds the claim or withdraws it.

Item 6 on the list needs no library at all and is the one to do first anyway:
the closure challenge preprint, arXiv `2603.28884`. The submission draft quotes
a permission from it that is nowhere on this machine.

**Unblock:** open the list, work the entries top down, and paste back the
section named beside each. Nothing else in the reading program waits on this.
