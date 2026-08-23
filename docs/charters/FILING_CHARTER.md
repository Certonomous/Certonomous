# FILING CHARTER — where things go, and what they are called

Adopted 2026-08-18 at Sanaa's instruction, immediately after the reorganisation
that collapsed a 4,924-file webroot to 10 tracked files and rehomed roughly
8,000 files across six directory renames. Her instruction, verbatim:

> when you save md files, log files, charters, run trees anythig, make sure to
> respect our organization and naming convention now so that our folders and
> later our repos are always clean and organized and we dont have to go through
> the deep cleaning and reorganization again.

**This charter is enforced by `scripts/check_filing.py`, and the script is the
binding artifact.** This page exists so a human can read the rules; the script
exists so nobody can quietly stop following them. Where the two disagree, that
is a defect in one of them and a docket item, not a matter of interpretation.

## 1. Why this is a script and not only a page

The convention described below was already **near-universal before it was ever
written down** — at adoption, 51 of 51 documents directly in `docs/` were in
UPPER_SNAKE, and 70 of 72 entries in `scripts/` were lower_snake. The tree drifted
into needing a multi-day clean-up anyway.

That is the whole argument. A convention that is documented, obeyed by a large
majority, and **measured by nothing** decays silently, because every individual
departure is defensible and no one is counting. **A rule nobody can fail is a
preference.** The check is what converts this page from a preference into a rule.

## 2. The rules

| ID | Rule | Rationale |
| --- | --- | --- |
| **R0** | Every path is ASCII letters, digits, dot, underscore, hyphen. No spaces, no accented characters. | A space breaks every unquoted shell loop in this lab, and a non-ASCII character makes a file unfindable by anyone typing its name from a printed page. |
| **R1** | Nothing loose at a repository root. Only `README.md`, `.gitignore`, `.gitattributes`, and themed directories. | This is the class Sanaa named first: "i dont want random pngs everywhere random scripts etc". |
| **R2** | Documents directly in `docs/` are `UPPER_SNAKE_CASE.md`. | 51 of 51 at adoption. |
| **R3** | Executables in `scripts/` are `lower_snake.py` or `lower_snake.sh`. | 70 of 72 at adoption. |
| **R5** | Assets in `media/` and `research/` live in a themed subdirectory, never loose in the parent. | `media/plots/`, `media/acts/`, `media/gui-proof/`, `research/closure/`. |
| **R6** | An OpenFOAM case lives under `verification/runs/<CAMPAIGN>/`, `cases/`, or `models/`. | Never beside the prose describing it. `models/` holds reference case *definitions* (inputs); `verification/runs/` holds run *outputs*. |
| **R7** | Campaign records are `<RUNG>_<PURPOSE>.md`; helper code inside a campaign directory is `lower_snake.py`. | `K0c_RESULTS.md`, `K2a_RACK_ROW_MODULE_SPEC.md`, `digitize_wibron2018.py`. A rung identifier carries lowercase — `K0c`, `K0cT`, `K2b`, `KV1`. |
| **R8** | Papers are `author_year_identifier.pdf` with a matching `.txt` sidecar, filed under a topic subdirectory of `docs/papers/`. | The year is what distinguishes two papers by the same group. The `.txt` sidecar is what lets an agent grep contents without re-parsing the PDF, so **a PDF and its sidecar always travel together.** |

## 3. Documented exceptions, each with its reason

An exception with a stated reason is a rule. An exception without one is drift,
and the difference is the whole point of this section.

- **`scripts/auto-stop.sh`** keeps its hyphen. It is installed to
  `/usr/local/bin/auto-stop.sh` and `scripts/installed_registry.py` compares the
  two **by md5**; renaming the tracked copy would break that identity check.
- **`models/tmr/**`** holds solver cases outside a run tree. They are reference
  case definitions rather than run outputs, and `models/tmr` is referenced by
  path in five code files. The first draft of R6 flagged all fourteen of them;
  **the rule was wrong, not the tree**, and it was corrected rather than the
  files moved. Recorded because it is the exact shape of error this charter
  could otherwise cause: satisfying a freshly written rule by breaking working
  code.

## 4. Deferred, and why — coupling is measured before anything moves

Four filings violate the rules above and were **deliberately not corrected on
adoption day**, because `docs/LESSONS.md` records that a webroot move broke 178
code files and that git rename detection is useless at this coupling. Each was
measured before the decision:

| Path | References | Disposition |
| --- | --- | --- |
| `media/LAPTOP_SHOOT.md` | 34 files | Move with a coordinated re-point, in a dedicated batch. |
| `media/FILMING_COMMANDS.md` | 15 files | Same. |
| `media/valve.png` | 3 files | Same batch. |
| `media/Gui_issue.png` | 2 files | Same batch. |

Eight assets in the same directory carried **zero** references and were filed to
`media/plots/` immediately. The difference between the two groups was measured,
not assumed.

## 5. What a new record does

Before writing any durable file, find the nearest existing sibling and copy its
pattern. If no sibling exists, the file probably belongs in a directory that
already has one. Then run:

```
python3 scripts/check_filing.py            # the tree
python3 scripts/check_filing.py --selftest # the instrument
```

**Run the selftest whenever a rule is edited.** A rule change invalidates the
previous green: the planted controls are what establish that the check still
catches what it claims to, and this lab has been misled three separate times by
a check whose population was empty and which therefore reported a clean zero.

## 6. Provenance of this charter's own rules

Every threshold above was **measured on the tree at adoption**, not chosen.
The counts in §2 and the reference counts in §4 are readings, reproducible with
`git -c core.quotePath=false ls-tree -r HEAD --name-only` and `grep -rIl`.
They are not constants: re-derive rather than quote.

Two defects in the check itself were caught by its own controls before it ever
ran on the tree, and both are recorded here because they generalise. The first:
the campaign-record rule rejected `K0c_RESULTS.md`, the most canonical filename
in the campaign, because rung identifiers carry lowercase. The second: `git
ls-tree` **escapes non-ASCII paths by default**, so the rule that exists to catch
non-ASCII names never saw a non-ASCII character until `core.quotePath=false` was
set — a check can be blinded by the instrument that feeds it, and the planted
control is what exposed it.

## Amendment record (appended 2026-08-23): silent-background convention (2026-08-23)

This charter previously carried no amendment record; this section starts
one, append-only.

**Dated addendum, 2026-08-23, appended at the foot; append-only. One standing
convention added on the owner's directive. No clause above is altered, widened
or narrowed; no line above this section changed number; this charter carries no version
line and none is added, because this addendum inserts nothing and
edits nothing above itself.**

Sanaa's directive, verbatim (2026-08-23): "There needs to be added to all
the .md convention files that all agents must always act in a silent way on
the background without showing bash or ssh on the screen, the screen must
always remain clean with only discussion and results."

In force for every agent this charter binds, and recorded lab-wide as
`CLAUDE.md` rule 16: all heavy work (bash, ssh, compute, file surgery) runs
inside background lanes or subagents, never as top-level tool calls in the
user-facing session when avoidable; user-facing reports carry discussion,
numbers and verdicts only, never pasted terminal output, raw logs or command
transcripts (quote the specific value with its artifact path, not the dump it
came from); supervisors enforce this on their lanes, condensing a transcript
before relay rather than forwarding it raw. Honest caveat: the Claude Code UI
renders whatever tool calls the top-level session makes, so the convention is
kept by pushing work into background agents; that delegation, not a display
setting, is what keeps the screen clean.

| what the amendment did | figure |
| --- | --- |
| standing conventions added | 1 |
| clauses altered, widened or narrowed | 0 |
| lines whose number changed above this section | 0 |
