# CHECK 1 — `run_f28_candidate.sh`, the section 11.1 guard-virgin wiring, read as a diff AND exercised, by `cfd-supervisor` personally

**Date:** 2026-08-31 (22:20Z). **Subject:**
`cases/F28_DUCTED_ACTUATOR_DISK/run_f28_candidate.sh`, md5
`e02bfa8340147261d743973effe2e34d`. **Superseded:** `run_f28.sh`, md5
`24683bf8e5953c87d735ad993aac56f2` — **re-hashed by me at read time, and
`git diff --stat HEAD` on it is empty**, so the live launcher is untouched and
the diff I read is the diff that exists. **Diff:** 3 hunks, 109 lines added,
**0 removed**. **Not installed. Stage 1 still gated.**

This is gate (b) of the three named in `CHECK1_ANALYSE_F28_CANDIDATE.md` §"What
this does not do". It is **one of two**; the other — Addendum 3's floored
criterion — is not discharged by this record.

## VERDICT OF THE READ: the wiring is sound and correctly positioned. It does not by itself open Stage 1.

Both halves, because a read alone is not the whole of check 1 — this team
certified a permanently blind guard twice at supervisor level tonight and only
running it caught that (`9c223449`):

1. **I read the diff**, all three hunks, in full.
2. **I exercised it with cases I wrote myself**, not by re-running the lane's
   suite. Re-running the lane's suite would prove the lane's suite passes.
   `supervisor_check_guard_wiring.sh`, filed beside this record: **11 limbs, 11
   PASS, 0 FAIL.**

## WHAT I READ

- **Hunk 1 (`@@ -126,6`)** defines `guard_virgin_section_11_1` immediately after
  `abort()`. It resolves the instrument as `$REPO/cases/$CASE_ID/analyse_f28.py`,
  the same shape as `$CHECKER` at :285, tests `-x`, saves and restores `PHASE`,
  and calls `python3 "$analyser" --guard-virgin "$target"` **without redirecting
  stderr**, so the refusal's reason reaches the operator rather than `/dev/null`.
- **Hunk 2 (`@@ -217,6`)** puts the call inside the `--preflight` branch, before
  that branch's own `mkdir -p "$RUN_DIR"`.
- **Hunk 3 (`@@ -226,6`)** puts the call at the registered position: **after
  `PHASE="assemble"`, before the `mkdir` that creates `$RUN_DIR/0`.** Verified in
  the file rather than in the diff: the guard is line **346**, the `mkdir` line
  **347**; in the preflight branch, **329** and **330**.
- **`bash -n` clean.**

**The `set -e` hazard I went looking for is not present, and I checked before
believing the control.** The pattern `python3 …; rc_zero=$?` would abort the
script before the assignment under `errexit`. `run_f28.sh` carries only
`set -o pipefail` (:54) and a `set +u`/`set -u` pair around the OpenFOAM
sourcing (:423/:426, after both call sites); the file's own note at :44-45 says
`set -e` deliberately does not gate here. So the exit-code capture is safe. Had
`errexit` been on, the lane's extracted-fragment harness would very likely still
have passed while the real launcher aborted on its first probe.

## WHAT THE EXERCISE PROVED — MY OWN MATRIX

Every limb drives the function **extracted verbatim from the candidate launcher**
(the harness prints the source md5 it extracted from, `e02bfa83…`), under a
synthetic `$REPO` tree, with a real `python3` comparator underneath.

| Limb | Comparator | Case state | Result |
|---|---|---|---|
| `live_cannot_distinguish` | **currently installed** `analyse_f28.py` | virgin | **rc 1, `CANNOT DISTINGUISH`** |
| `cand_virgin_exists` | candidate | virgin, exists | rc 0, `VIRGIN` |
| `cand_absent` | candidate | does not exist | rc 0, `VIRGIN` |
| `cand_has_zero` | candidate | carries `0/` | rc 1, `GUARD REFUSED` |
| `cand_has_time` | candidate | carries `250/` | rc 1, `GUARD REFUSED` |
| `cand_frac_time` | candidate | carries `0.5/` | rc 1, `GUARD REFUSED` |
| `cand_postproc_ok` | candidate | carries `postProcessing/` | **rc 0, `VIRGIN`** |
| `planted_blind_zero` | stub, always exit 0 | carries `0/` | rc 1, `GUARD IS BLIND` |
| `planted_always_two` | stub, always exit 2 | virgin | rc 1, `CANNOT DISTINGUISH` |
| `no_instrument` | absent | virgin | rc 1, `has no instrument` |
| `probe_tree_cleanup` | — | — | 0 probe trees left behind |

**Three of these the lane did not run, and they are the three I most wanted.**

- **`cand_postproc_ok` — the over-refusal limb.** A guard that refuses *any*
  subdirectory would refuse every legitimate assemble the moment anything
  non-temporal appeared, and would be discovered only by blocking real work. The
  guard discriminates time directories from non-time directories. **A guard is
  wrong if it fires when it should not, not only if it fails to fire**, and the
  lane's matrix tested only the second failure direction.
- **`cand_frac_time`** — `0.5/` is a time directory and is refused; a
  purely-integer test would have missed it.
- **The side-effect assertion**, run on every `absent` limb: the guard must never
  create the directory it inspects. It does not.

**The planted controls are behavioural — three exit codes — never a text match on
the guard's own message.** Matching the message is precisely the defect class
that produced `9c223449`, where a banner comment quoting the entry verbatim
satisfied the reader.

## THE FINDING I RATE HIGHEST, AND IT IS THE LANE'S

**The wiring FAILS CLOSED against the tree as it stands today, and is inert until
the comparator candidate is installed.** The installed `analyse_f28.py` carries
`guard_virgin_case` at :397 but **no `--guard-virgin` entry point**, so it exits
**2 on a virgin directory as well as on a dirty one** — a usage error wearing a
refusal's exit code. A naive `|| abort` would have read that as a refusal and
reported a guard that was watching nothing. My `live_cannot_distinguish` limb
reproduces it independently: **rc 1, `CANNOT DISTINGUISH`**, at zero compute.

This is the correct behaviour and it is worth stating why. **A blanket exit 2 is
indistinguishable from a working guard unless something drives the negative
limb.** The whole planted-zero principle (`CLAUDE.md` rule 3) is that a refusal
from a reader not shown able to *accept* is not evidence, exactly as a zero from
a reader not shown able to see a non-zero is not evidence. This function applies
that principle to itself on every invocation, for ~132 ms.

## WHAT THIS DOES NOT DO

- **It does not install.** `run_f28.sh` is untouched at `24683bf8…`.
- **It does not open Stage 1.** Gate (c), Addendum 3's floored stationarity
  criterion actually wired with its own check-1 read, is outstanding.
- **It cannot function until the comparator candidate is installed**, and it says
  so by aborting rather than by passing quietly. The two land together.
- **No number is graded by any of this.** It is an instrument control on a
  launcher guard. No verdict attaches to it and none is claimed.

## COST

Zero solver core-minutes. Sub-second CPU for the lane's suite and mine.

*Read and exercised by `cfd-supervisor` personally, not delegated and not
relayed. The 11/11 is my own measurement in my own shell, from the harness filed
beside this record; the lane's own 21/21 is recorded as the lane's and is not
what this verdict rests on.*
