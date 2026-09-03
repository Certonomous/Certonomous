#!/usr/bin/env python3
"""Plant + mutation proof for the `corrects:[...]` field in `append_record.py`.

Sanaa's PLUMBING AMENDMENT, 2026-09-03 (ruling 1 of
`etc/sessions/2026-09-03T1600Z_sanaa_five_rulings.md`): a tool-allocated id is
accepted SOLELY inside a structured `corrects:` field on a correction row;
refusal is unchanged everywhere else; the side-file is retired.

WHY THIS FILE IS TRACKED. A kill table quoted in a commit message expires the
moment it is written -- the next reader cannot re-run it (D173). The proof is a
file a later reader can RUN, so it lives in `scripts/` beside the other
harnesses and not in a scratch directory (CLAUDE.md rule 13).

WHAT IS BEING PROVED, and a one-sided harness would prove none of it:

  * POSITIVE -- a correction row citing a tool-allocated id inside a structured
    `corrects:[...]` field is ACCEPTED and the FULL id is readable in the bytes
    on disk afterwards. That is the whole point: the pre-amendment workaround
    degraded an exact key to a description.
  * REFUSAL UNCHANGED EVERYWHERE ELSE -- every other route by which a tool-form
    id can reach the rows still refuses at exit 9 and leaves the record
    BYTE-IDENTICAL. This is a property of the CONSTRUCTION, not a claim:
    acceptance is implemented as a MASK over the one existing smuggle scan, so
    there is one scan and one message and the amendment only decides what it
    sees.
  * NEAR-MISS -- the scoping is TIGHT, not merely permissive: a citation field
    on a non-correction row, a malformed body, an unterminated field, an empty
    field and a field on a row with no id of its own all refuse.
  * MUTATION (knobs) -- each clause is removed in turn through a knob the
    production entry point never passes, and the limb it guards must FLIP. A
    positive that still passes with the amendment removed is testing nothing.
  * MUTATION (source) -- CELL H, the C3 HARDENING. See below. This one mutates
    the SOURCE, because the clause it defends has no knob and must not get one.
  * PLANTED ZERO -- before any refusal is believed, the reader is shown able to
    SEE the id in that fixture. A refusal that failed to fire and a scan that
    could not see the id look identical from the outside (CLAUDE.md rule 3).

CELL H -- THE C3 HARDENING, AND WHY IT NEEDED ITS OWN MUTANT. Clause C3 decides
whether a correction row carries its OWN id at its own entry position. It first
read `entry.search(line)` -- the RAW line, which still carries the cited id
inside its `corrects:[...]` field -- so the CITATION was itself a candidate for
satisfying "this row has its own id". It could not win, and only because every
pattern in `RECORDS` happens to be `^`-anchored: under `re.M` on a single line
`^` matches at position 0 alone. The clause was correct BY A PROPERTY OF A
DIFFERENT CONSTANT. VERIFICATION_CHARTER §2p.5 -- a repair that changes which
coincidence you depend on is not a repair -- so C3 now searches the MASKED line,
where the citation is blanked to same-length spaces and cannot be a candidate
under ANY pattern, anchored or not. Cell H drives a DELIBERATELY UNANCHORED
record pattern, which is the loosening the old clause could not survive, and
requires the arm to FLIP: the pre-hardening source ACCEPTS the row, the hardened
source REFUSES it. An arm that passes against both versions would not be
evidence of the hardening, and the cell asserts its own mutation landed (exactly
one textual replacement) before believing either side.

THE MUTANT NEVER TOUCHES THE WORKING TREE. Agents share this checkout. Every
cell imports from a TEMP COPY of the subject; the mutated cell copies again and
edits the copy. The subject's sha256 is asserted unchanged at the end, in a
`finally`. `__pycache__` is purged in the copy before every import: the stale-
bytecode inversion has made a clean control fail and a mutated case pass in this
lab, and `PYTHONDONTWRITEBYTECODE` does NOT fix it.

Run:  python3 scripts/mutation_harness_append_record_corrects.py
      python3 scripts/mutation_harness_append_record_corrects.py \
              --module <dir>     # grade some other scripts/ directory
Exit: 0 when every arm holds AND cell H flips; 1 otherwise.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _find_repo() -> Path:
    """The checkout whose live records the N11 corpus arms read.

    Resolved by LOOKING FOR THE RECORDS rather than by assuming this file's
    parent, so the harness reads the same corpus whether it is run from
    `scripts/` (where it lives) or from a staging directory during review. A
    harness that silently read a different DOCKET would make N11 a coin flip.
    """
    for base in (HERE, *HERE.parents, Path.cwd(), *Path.cwd().parents):
        if (base / "docs" / "DOCKET.md").is_file():
            return base
    raise SystemExit(
        "REFUSED: no checkout containing docs/DOCKET.md was found above "
        f"{HERE} or {Path.cwd()}. The N11 live-corpus arms have no corpus to "
        "read, and an arm with no population is not an arm.")


REPO = _find_repo()

#: Everything the subject imports from its own tree, plus the subject.
SUBJECT = "append_record.py"
COMPANIONS = ("control_kind.py",)

#: The one source line cell H reverts, and what it reverts it to. Both are
#: matched LITERALLY and the replacement count is asserted to be exactly 1 --
#: a mutation that silently did not land would make the cell vacuous, which is
#: the failure mode a mutation harness exists to avoid.
C3_HARDENED = ("        own = (ALLOCATE_PLACEHOLDER in line) or "
               "bool(entry.search(masked_line))")
C3_PRE = ("        own = (ALLOCATE_PLACEHOLDER in line) or "
          "bool(entry.search(line))")

PATH = "docs/COST_CALIBRATION.md"
DOCKET = "docs/DOCKET.md"

SEED = ("| id | date | team | process |\n|---|---|---|---|\n"
        "| C-1 | 2026-09-03 | verification | a seeded LEGACY row |\n")
SEED_D = ("| # | Item | Where found | What settles it |\n"
          "|---|------|-------------|-----------------|\n"
          "| D1 | a seeded LEGACY docket row | here | nothing |\n")

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


# ------------------------------------------------------------- plumbing
def stage(dest: Path, src_dir: Path) -> Path:
    """A temp copy of the subject and its companions. Never the live tree."""
    dest.mkdir(parents=True, exist_ok=True)
    for name in (SUBJECT, *COMPANIONS):
        shutil.copy2(src_dir / name, dest / name)
    purge_pycache(dest)
    return dest


def purge_pycache(root: Path) -> None:
    for pyc in root.rglob("__pycache__"):
        shutil.rmtree(pyc, ignore_errors=True)


def git(repo: Path, *args: str) -> None:
    done = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, env=ENV)
    if done.returncode != 0:
        raise RuntimeError(f"git {args[0]}: {done.stderr.strip()[:300]}")


def make_repo(td: Path, path: str, seed: str, tag: str = "") -> Path:
    repo = td / ("repo" + tag + "_" + path.replace("/", "_"))
    (repo / "docs").mkdir(parents=True)
    (repo / path).write_text(seed)
    subprocess.run(["git", "init", "-q", str(repo)], capture_output=True,
                   text=True, env=ENV, check=True)
    git(repo, "config", "user.email", "control@certonomous.invalid")
    git(repo, "config", "user.name", "corrects plant harness")
    git(repo, "config", "commit.gpgsign", "false")
    git(repo, "add", "--", path)
    git(repo, "commit", "-q", "-m", "seed")
    return repo


# ----------------------------------------------------- CELL H, the probe
#: Driven in a SUBPROCESS against one staged module directory, so the hardened
#: and pre-hardening sources are never both resident in one interpreter (each
#: does load-time asserts and a `sys.path` insert). Prints one JSON line.
H_TARGET = "C-20260902T215932.385336Z-ef920ed2"
#: THE LOOSENING. Exactly `RECORDS['docs/COST_CALIBRATION.md']` with its `^\|`
#: head and trailing `\|` removed -- an id pattern that parses this record's own
#: id vocabulary but is UNANCHORED. `C-\d+` matches `C-20260902`, the digit run
#: inside the cited tool id, so under this pattern the CITATION is a candidate
#: for the row's own id on the raw line and is not one on the masked line.
H_UNANCHORED = r"(C-\d+)"
H_CORR = "**CORRECTION ROW, naming the row it corrects"
#: The fixture: a correction row whose ID CELL IS EMPTY. Its only id anywhere is
#: the citation.
H_ROW_NO_OWN_ID = (f"| | 2026-09-03 | heat-transfer | {H_CORR}: "
                   f"corrects:[{H_TARGET}] | a | b | c |\n")


def h_probe_body() -> dict:
    import append_record as AR
    out: dict = {}
    ph = AR.ALLOCATE_PLACEHOLDER
    # The loosening is applied to the module's own table at call time --
    # `scan_corrects` compiles `RECORDS[path]` per call, so this is the same
    # code path a future editor would take by loosening the constant.
    out["anchored_pattern_was"] = AR.RECORDS[PATH]
    AR.RECORDS[PATH] = H_UNANCHORED

    # H0 -- PLANTED ZERO for the whole cell. Under the loosened pattern the
    # citation MUST be visible on the raw line, or H1 proves nothing: a clause
    # that refuses because its reader is blind is not a clause that guards.
    entry = re.compile(AR.RECORDS[PATH], re.M)
    out["h0_raw_line_carries_a_parsable_id"] = bool(
        entry.search(H_ROW_NO_OWN_ID))
    out["h0_id_cell_is_empty"] = H_ROW_NO_OWN_ID.split("|")[1].strip() == ""

    # H1 -- THE FLIP. `scan_corrects` in isolation (the mechanism) ...
    r = AR.scan_corrects(H_ROW_NO_OWN_ID, PATH)
    out["h1_scan_corrects_ok"] = bool(r["ok"])
    out["h1_reason_names_entry_position"] = (
        "entry position" in (r["reason"] or ""))
    out["h1_code"] = r["code"]
    # ... and `check_allocation` end to end (the consequence: whether the row
    # would LAND with the cited id as the only id in the line).
    out["h1e_check_allocation_ok"] = bool(
        AR.check_allocation(H_ROW_NO_OWN_ID, PATH, allocate=False)["ok"])

    # H2 -- NO OVER-REFUSAL, placeholder limb. Same loosened pattern, but the
    # row carries `{{ALLOCATE_ID}}`. Must be ACCEPTED by both versions: masking
    # cannot hide a placeholder, because the body parse admits tool-allocated
    # ids and nothing else.
    row_ph = (f"| {ph} | 2026-09-03 | heat-transfer | {H_CORR}: "
              f"corrects:[{H_TARGET}] | a | b | c |\n")
    out["h2_placeholder_row_ok"] = bool(AR.scan_corrects(row_ph, PATH)["ok"])

    # H3 -- NO OVER-REFUSAL, real-own-id limb. Same loosened pattern, and the
    # row's id cell carries a genuine LEGACY id. The mask must not blind the
    # clause to an id that really is the row's own.
    row_own = (f"| C-2 | 2026-09-03 | heat-transfer | {H_CORR}: "
               f"corrects:[{H_TARGET}] | a | b | c |\n")
    out["h3_legacy_own_id_row_ok"] = bool(AR.scan_corrects(row_own, PATH)["ok"])

    # H4 -- the ANCHORED pattern, restored, on the SAME fixture. Both versions
    # refuse here, and that is exactly the point: this is the arm N8 already
    # drives, and it cannot distinguish the two sources. Recorded so the report
    # states plainly WHICH arm carries the hardening.
    AR.RECORDS[PATH] = out["anchored_pattern_was"]
    out["h4_anchored_same_fixture_ok"] = bool(
        AR.scan_corrects(H_ROW_NO_OWN_ID, PATH)["ok"])
    return out


def h_probe(module_dir: Path) -> dict:
    done = subprocess.run(
        [sys.executable, "-B", str(Path(__file__).resolve()),
         "--h-probe", "--module", str(module_dir)],
        capture_output=True, text=True, env=ENV)
    if done.returncode != 0:
        return {"probe_error": (done.stderr or done.stdout).strip()[:400]}
    for ln in reversed(done.stdout.splitlines()):
        if ln.startswith("{"):
            return json.loads(ln)
    return {"probe_error": "no JSON line from the probe"}


# ------------------------------------------------------------- the arms
def run_arms(AR, table_record) -> None:
    """The 27 pre-existing arms. `AR` is the imported subject module."""
    ph = AR.ALLOCATE_PLACEHOLDER
    record = table_record

    def run_main(repo: Path, path: str, rows: str, *extra: str):
        f = repo.parent / (repo.name + ".rows.md")
        f.write_text(rows)
        o, e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
            rc = AR.main(["--path", path, "--rows", str(f), "--repo", str(repo)]
                         + list(extra))
        return rc, o.getvalue() + e.getvalue()

    with tempfile.TemporaryDirectory(prefix="corrects_plant_") as tdname:
        td = Path(tdname)
        repo = make_repo(td, PATH, SEED)

        # ============ ARM P0 -- ESTABLISH A REAL TARGET ID ==================
        # The row every citation below names is written by main() itself and
        # its id is read back off disk. Nothing here is a fixture id.
        rc, _ = run_main(repo, PATH,
                         f"| {ph} | 2026-09-03 | heat-transfer | the row that "
                         f"will be corrected |\n", "--allocate-id")
        disk = (repo / PATH).read_text()
        ids = re.findall(AR.tool_id_pattern(PATH), disk)
        record("P0 seed a real target row through main()",
               "rc=0, 1 tool id on disk",
               f"rc={rc}, {len(ids)} tool id on disk")
        if rc != 0 or len(ids) != 1:
            record("P0 GUARD the rest of the harness would be vacuous",
                   "reachable", "UNREACHABLE")
            return
        TARGET = ids[0]
        before_all = (repo / PATH).read_text()

        record("Z1 planted zero: ANY_TOOL_ID can SEE the target id",
               "seen", "seen" if re.findall(AR.ANY_TOOL_ID, TARGET) else "BLIND")

        CORR = "**CORRECTION ROW, naming the row it corrects"

        # ============ POSITIVE ARMS =========================================
        rows_p1 = (f"| {ph} | 2026-09-03 | heat-transfer | {CORR}: "
                   f"corrects:[{TARGET}]. One cell corrected. | a | b | c |\n")
        rc, _ = run_main(repo, PATH, rows_p1, "--allocate-id")
        d1 = (repo / PATH).read_text()
        record("P1 correction row citing a tool id in corrects:[] -- ACCEPTED",
               "rc=0", f"rc={rc}")
        record("P1b the FULL cited id is greppable in the bytes on disk",
               "present", "present" if TARGET in d1 else "ABSENT")
        record("P1c the record actually changed (the writer can write)",
               "changed", "changed" if d1 != before_all else "UNCHANGED")
        # P1d -- THE CLAIM THAT DECIDES WHETHER THIS IS SAFE FOR THE READERS.
        # After the citation lands the target id occurs TWICE in the bytes: once
        # as the P0 row's own id cell, once inside the correction row's field.
        # `parse_record_ids` -- the reader BOTH reconcilers import -- must count
        # it ONCE, or a correct correction row is reported as a duplicate id.
        record("P1d the CITED id occurs twice in the bytes and is ONE entry to "
               "the reader both reconcilers import",
               "2 occurrences, 1 entry",
               f"{d1.count(TARGET)} occurrences, "
               f"{AR.parse_record_ids(d1, PATH).count(TARGET)} entry")
        record("P1e the record now holds 3 entries: the legacy seed, the target "
               "row and the correction row",
               "3 entries", f"{len(AR.parse_record_ids(d1, PATH))} entries")

        ids_now = AR.parse_record_ids(d1, PATH)
        two = [i for i in ids_now if AR.is_tool_id(i)]
        if len(two) < 2:
            record("P2 two ids in one corrects:[a;b] field -- ACCEPTED",
                   "rc=0, both on disk",
                   "UNREACHABLE -- P1 was refused, so no second id exists")
            two = two * 2 if two else ["C-NONE"] * 2
        rows_p2 = (f"| {ph} | 2026-09-03 | heat-transfer | {CORR}: "
                   f"corrects:[{two[0]};{two[1]}] both rows | a | b | c |\n")
        rc, _ = run_main(repo, PATH, rows_p2, "--allocate-id")
        d2 = (repo / PATH).read_text()
        record("P2 two ids in one corrects:[a;b] field -- ACCEPTED",
               "rc=0, both on disk",
               f"rc={rc}, "
               f"{'both' if two[0] in d2 and two[1] in d2 else 'NOT both'} "
               f"on disk")

        repo_d = make_repo(td, DOCKET, SEED_D, "d")
        rows_p3 = (f"| {ph} | 2026-09-03 | heat-transfer | **CORRECTION ROW — "
                   f"it corrects the calibration row corrects:[{TARGET}] "
                   f"across records | settled |\n")
        rc, _ = run_main(repo_d, DOCKET, rows_p3, "--allocate-id")
        dd = (repo_d / DOCKET).read_text()
        record("P3 CROSS-RECORD: a DOCKET correction row citing a C- id",
               "rc=0, id on disk",
               f"rc={rc}, {'id on disk' if TARGET in dd else 'ABSENT'}")

        repo_l = make_repo(td, PATH, SEED, "l")
        rows_p4 = (f"| C-2 | 2026-09-03 | heat-transfer | {CORR}: "
                   f"corrects:[{TARGET}] | a | b | c |\n")
        rc, _ = run_main(repo_l, PATH, rows_p4, "--expect-first-id", "C-2")
        record("P4 a LEGACY-id correction row citing a tool id -- ACCEPTED",
               "rc=0", f"rc={rc}")

        # ============ REFUSAL ARMS (refusal unchanged everywhere else) =======
        base = (repo / PATH).read_text()

        def refuse(arm: str, rows: str, *extra: str, expect: int = 9) -> None:
            # Planted zero per fixture: the scan must be able to SEE an id here.
            seen = bool(re.findall(AR.ANY_TOOL_ID, rows))
            rc, _ = run_main(repo, PATH, rows, *extra)
            same = (repo / PATH).read_text() == base
            record(arm, f"rc={expect}, unchanged, id visible",
                   f"rc={rc}, {'unchanged' if same else 'RECORD CHANGED'}, "
                   f"{'id visible' if seen else 'SCAN BLIND'}")

        refuse("N1 hand-written tool id in the ID CELL, no field",
               f"| {TARGET} | 2026-09-03 | heat-transfer | a row | a | b | c |\n")
        refuse("N2 hand-written tool id in PROSE, no field (the 2026-09-02 case)",
               f"| {ph} | 2026-09-03 | heat-transfer | it corrects `{TARGET}` "
               f"in prose | a | b | c |\n", "--allocate-id")
        refuse("N3 NEAR-MISS: corrects:[] field on a NON-correction row",
               f"| {ph} | 2026-09-03 | heat-transfer | an ordinary row "
               f"corrects:[{TARGET}] | a | b | c |\n", "--allocate-id")
        refuse("N4 NEAR-MISS: unterminated corrects:[ field on a correction row",
               f"| {ph} | 2026-09-03 | heat-transfer | {CORR}: "
               f"corrects:[{TARGET} | a | b | c |\n", "--allocate-id")
        refuse("N5 NEAR-MISS: malformed body -- prose inside the field",
               f"| {ph} | 2026-09-03 | heat-transfer | {CORR}: "
               f"corrects:[see {TARGET} maybe] | a | b | c |\n", "--allocate-id")
        refuse("N6 a valid field AND a second hand-written id elsewhere in the row",
               f"| {ph} | 2026-09-03 | heat-transfer | {CORR}: "
               f"corrects:[{TARGET}] and also {TARGET} loose | a | b | c |\n",
               "--allocate-id")
        refuse("N7 C3: the row's OWN id cell is a hand-written tool id",
               f"| {TARGET} | 2026-09-03 | heat-transfer | {CORR}: "
               f"corrects:[{TARGET}] | a | b | c |\n")
        refuse("N8 C3: a valid field on a correction row with NO id of its own",
               f"| | 2026-09-03 | heat-transfer | {CORR}: "
               f"corrects:[{TARGET}] | a | b | c |\n")
        refuse("N9 NEAR-MISS: an EMPTY corrects:[] field",
               f"| {ph} | 2026-09-03 | heat-transfer | {CORR}: corrects:[] and "
               f"{TARGET} | a | b | c |\n", "--allocate-id")
        refuse("N10 CROSS-PREFIX: an L- tool id hand-written in a C- record",
               f"| {ph} | 2026-09-03 | heat-transfer | see "
               f"L-20260831T154707.481920Z-a3f91c4d | a | b | c |\n",
               "--allocate-id")

        # N11 -- the LIVE corpus negative. docs/DOCKET.md carries one line with
        # the string `CORRECTION ROW` that is NOT a correction row: it opens
        # `**A CORRECTION ROW CANNOT NAME...`. The anchor must exclude it, or a
        # real row in a real record would be classified as a correction row.
        live = (REPO / DOCKET).read_text()
        live957 = [l for l in live.splitlines() if "CORRECTION ROW" in l]
        _cm = getattr(AR, "CORRECTION_MARKER", None)

        def pat_for(p: str) -> str:
            """This record's declaration, or a NEVER-MATCHING pattern.

            `CORRECTION_MARKER` does not exist on the pre-amendment module, and
            a harness that crashes there grades nothing. `(?!)` is the honest
            stand-in: it matches no line, so every marker arm reads as "the
            marker matched nothing", which is the truth about a module that has
            no marker.
            """
            return _cm[p] if _cm else r"(?!)"

        marker = re.compile(pat_for(DOCKET))
        # N11 -- IDENTITY, not a count: the NAMED live line must be in the
        # corpus and must NOT be matched. A count here would go red the day a
        # peer writes a second prose mention, which is not what this tests.
        named = [l for l in live957 if "CORRECTION ROW CANNOT" in l]
        record("N11 LIVE corpus: the DOCKET line 'A CORRECTION ROW CANNOT...' "
               "is present and is NOT matched by the anchored marker",
               "present=True, matched=0",
               f"present={len(named) >= 1}, "
               f"matched={sum(1 for l in named if marker.search(l))}")
        livec = (REPO / PATH).read_text()
        lc = [l for l in livec.splitlines() if "CORRECTION ROW" in l]
        mc = re.compile(pat_for(PATH))
        # N11b -- PLANTED ZERO for N11, AS A PROPERTY AND NOT AS A COUNT.
        # REPAIRED 2026-09-03. This arm read `17 of 17`, a literal measured
        # against the corpus of the hour. It went RED within twenty minutes,
        # when an ansys-verification row landed (commit 1b856233) whose entry
        # cell opens `**VMFL046 — ...` and says `CORRECTION ROW IN SUBSTANCE`
        # 718 characters in. NOTHING WAS WRONG WITH THE MARKER: that row is
        # excluded for exactly the reason DOCKET's is. What was wrong was the
        # arm, which asserted a COUNT where it meant an IDENTITY -- the failure
        # `mutation_harness_docket_reconciliation` names in its own opening
        # ("a probe survived an inverted comparison because it asserted a COUNT
        # rather than an IDENTITY"). A count-shaped arm over a corpus peers
        # append to goes red on a commit that changed nothing it was testing,
        # and the honest repair is to assert the property.
        n_mc = sum(1 for l in lc if mc.search(l))
        record(f"N11b PLANTED ZERO for N11: the anchored marker is NOT vacuous "
               f"-- it matches live COST_CALIBRATION correction rows [census "
               f"at this run: {n_mc} matched of {len(lc)} lines carrying the "
               f"string; the census is REPORTED, never asserted]",
               "matched >= 1: True", f"matched >= 1: {n_mc >= 1}")
        # N11c -- the IDENTITY arm. Every live line in EITHER record that
        # carries the string and is NOT matched must be excluded for the STATED
        # reason: the declaration is not at the HEAD of the entry cell. An
        # unmatched line that could not be explained that way would be a real
        # under-match and this arm would name it.
        def entry_cell_opens_with_declaration(line: str) -> bool:
            cells = line.split("|")
            if len(cells) < 5:
                return False
            head = re.sub(r"^[ \t]*(?:\*\*|~~)*[ \t]*", "", cells[4])
            return bool(re.match(r"CORRECTION ROW\b", head))

        population = ([(l, pat_for(PATH)) for l in lc]
                      + [(l, pat_for(DOCKET)) for l in live957])
        unmatched = [l for l, pat in population
                     if not re.compile(pat).search(l)]
        explained = [l for l in unmatched
                     if not entry_cell_opens_with_declaration(l)]
        record("N11c IDENTITY: every live line carrying 'CORRECTION ROW' that "
               "the marker does NOT match is excluded because the declaration "
               "is not at the head of its entry cell",
               f"{len(unmatched)} unmatched, {len(unmatched)} explained",
               f"{len(unmatched)} unmatched, {len(explained)} explained")
        # N11d -- PLANTED ZERO for N11c. Its predicate must be able to return
        # True, or "every unmatched line is explained" is a sentence a predicate
        # that never fires would also satisfy.
        record("N11d PLANTED ZERO for N11c: the same predicate DOES fire on a "
               "row that opens its entry cell with the declaration",
               "fires: True",
               f"fires: {entry_cell_opens_with_declaration('| C-9 | d | t | **CORRECTION ROW, x | a |')}")

        # ============ MUTATION ARMS (knobs) -- each clause load-bearing ======
        ca = AR.check_allocation

        def ca_safe(rows, path, **kw):
            """The knobs do not exist on the pre-amendment module -- a
            TypeError there is itself the measurement, not a harness bug."""
            try:
                return ca(rows, path, **kw)
            except TypeError:
                return {"ok": None}

        record("M1 remove the amendment (apply_corrects=False): P1 must REFUSE",
               "refused",
               {True: "ACCEPTED", False: "refused",
                None: "KNOB ABSENT (pre-amendment module)"}[
                   ca_safe(rows_p1, PATH, allocate=True,
                           apply_corrects=False)["ok"]])
        record("M1b and WITH the amendment the same rows are accepted",
               "accepted",
               "accepted" if ca(rows_p1, PATH, allocate=True)["ok"]
               else "REFUSED")
        n3 = (f"| {ph} | 2026-09-03 | heat-transfer | an ordinary row "
              f"corrects:[{TARGET}] | a | b | c |\n")
        record("M2 remove C2 (require_correction_marker=False): N3 must be "
               "ACCEPTED -- so the correction-row scoping is load-bearing",
               "accepted",
               {True: "accepted", False: "REFUSED",
                None: "KNOB ABSENT (pre-amendment module)"}[
                   ca_safe(n3, PATH, allocate=True,
                           require_correction_marker=False)["ok"]])
        n8 = (f"| | 2026-09-03 | heat-transfer | {CORR}: "
              f"corrects:[{TARGET}] | a | b | c |\n")
        record("M3 remove C3 (require_own_entry=False): N8 must be ACCEPTED -- "
               "so the entry-position clause is load-bearing",
               "accepted",
               {True: "accepted", False: "REFUSED",
                None: "KNOB ABSENT (pre-amendment module)"}[
                   ca_safe(n8, PATH, allocate=False,
                           require_own_entry=False)["ok"]])
        record("M4 the smuggle guard itself is untouched: dropping it lets N1 "
               "through",
               "accepted",
               "accepted" if ca(f"| {TARGET} | x | y | z |\n", PATH,
                                allocate=False,
                                apply_smuggle_guard=False)["ok"] else "REFUSED")


# ------------------------------------------------------------------ main
def main(argv: list[str]) -> int:
    module_dir = HERE
    if "--module" in argv:
        module_dir = Path(argv[argv.index("--module") + 1]).resolve()

    # ---- the probe mode: one staged module, one JSON line, no arms.
    if "--h-probe" in argv:
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(module_dir))
        print(json.dumps(h_probe_body()))
        return 0

    subject = module_dir / SUBJECT
    before = hashlib.sha256(subject.read_bytes()).hexdigest()
    table: list[tuple[str, str, str, bool]] = []

    def record(arm: str, expected: str, observed: str) -> None:
        table.append((arm, expected, observed, expected == observed))

    try:
        with tempfile.TemporaryDirectory(prefix="corrects_stage_") as sd:
            staged = stage(Path(sd) / "hardened", module_dir)

            # ---- the 27 arms, in a subprocess-free import of the STAGED copy.
            sys.dont_write_bytecode = True
            sys.path.insert(0, str(staged))
            import append_record as AR  # noqa: E402
            run_arms(AR, record)

            # ---- CELL H: the hardened source vs the pre-hardening source.
            mutant = stage(Path(sd) / "pre_hardening", module_dir)
            src = (mutant / SUBJECT).read_text()
            n_hits = src.count(C3_HARDENED)
            record("H0a the C3 hardened line is present EXACTLY ONCE in the "
                   "subject (else the mutation below is vacuous)",
                   "1 occurrence", f"{n_hits} occurrence")
            (mutant / SUBJECT).write_text(src.replace(C3_HARDENED, C3_PRE))
            purge_pycache(mutant)
            back = (mutant / SUBJECT).read_text()
            record("H0b the mutation LANDED: the mutant carries the raw-line "
                   "clause and not the masked-line one",
                   "pre=1 hardened=0",
                   f"pre={back.count(C3_PRE)} hardened={back.count(C3_HARDENED)}")

            new = h_probe(staged)
            old = h_probe(mutant)
            for tag, r in (("hardened", new), ("pre-hardening", old)):
                if "probe_error" in r:
                    record(f"H probe ran ({tag})", "ran",
                           f"ERROR {r['probe_error']}")

            def g(r, k):
                return r.get(k, "MISSING")

            record("H0c PLANTED ZERO: under the loosened pattern the RAW line "
                   "really does carry a parsable id, and the id cell is empty",
                   "id parsable=True, cell empty=True",
                   f"id parsable={g(new,'h0_raw_line_carries_a_parsable_id')}, "
                   f"cell empty={g(new,'h0_id_cell_is_empty')}")

            # THE FLIP. This pair is the whole evidence for the hardening.
            record("H1 FLIP scan_corrects, unanchored pattern, citation is the "
                   "row's only id: PRE-HARDENING accepts",
                   "accepted", "accepted" if g(old, "h1_scan_corrects_ok") is True
                   else f"NOT accepted ({g(old,'h1_scan_corrects_ok')})")
            record("H1 FLIP scan_corrects, same fixture: HARDENED refuses",
                   "refused", "refused" if g(new, "h1_scan_corrects_ok") is False
                   else f"NOT refused ({g(new,'h1_scan_corrects_ok')})")
            record("H1r the hardened refusal is C3's own message and exit code",
                   "entry-position message, code 9",
                   f"{'entry-position message' if g(new,'h1_reason_names_entry_position') else 'OTHER message'}, "
                   f"code {g(new,'h1_code')}")
            record("H1e FLIP end to end (check_allocation): PRE-HARDENING would "
                   "LAND the row whose only id is the citation",
                   "accepted", "accepted" if g(old, "h1e_check_allocation_ok") is True
                   else f"NOT accepted ({g(old,'h1e_check_allocation_ok')})")
            record("H1e FLIP end to end (check_allocation): HARDENED refuses it",
                   "refused", "refused" if g(new, "h1e_check_allocation_ok") is False
                   else f"NOT refused ({g(new,'h1e_check_allocation_ok')})")

            # NO OVER-REFUSAL: the hardening must cost nothing on rows that do
            # carry their own id, under the same loosened pattern.
            record("H2 NO OVER-REFUSAL: placeholder row still accepted "
                   "(hardened)", "accepted",
                   "accepted" if g(new, "h2_placeholder_row_ok") is True
                   else f"REFUSED ({g(new,'h2_placeholder_row_ok')})")
            record("H3 NO OVER-REFUSAL: legacy-own-id row still accepted "
                   "(hardened)", "accepted",
                   "accepted" if g(new, "h3_legacy_own_id_row_ok") is True
                   else f"REFUSED ({g(new,'h3_legacy_own_id_row_ok')})")

            # H4 -- honesty about which arm carries the hardening. With the REAL
            # anchored patterns both sources refuse this fixture, so N8 cannot
            # distinguish them. Only H1 can.
            record("H4 with the REAL anchored pattern both sources refuse the "
                   "same fixture (hardened side shown; this is why N8 alone is "
                   "not evidence of the hardening)",
                   "refused", "refused" if g(new, "h4_anchored_same_fixture_ok")
                   is False else f"NOT refused ({g(new,'h4_anchored_same_fixture_ok')})")
            record("H4b and the pre-hardening source refuses it too -- the two "
                   "are INDISTINGUISHABLE on the anchored pattern",
                   "refused", "refused" if g(old, "h4_anchored_same_fixture_ok")
                   is False else f"NOT refused ({g(old,'h4_anchored_same_fixture_ok')})")
    finally:
        after = hashlib.sha256(subject.read_bytes()).hexdigest()
        if before != after:  # pragma: no cover - the tree was mutated in place
            print(f"REFUSED: the subject {subject} CHANGED during this run "
                  f"({before[:12]} -> {after[:12]}). The mutant is supposed to "
                  f"be a copy; a changed subject means a real file was held "
                  f"mutated and the whole table is void.")
            return 2

    return render(table, module_dir, before)


def render(table, module_dir: Path, sha: str) -> int:
    w = max(len(a) for a, *_ in table)
    print("=" * 118)
    print("PLANT + MUTATION KILL TABLE -- append_record corrects: field "
          "(Sanaa 2026-09-03)")
    print(f"subject: {module_dir / SUBJECT}  sha256 {sha[:16]}")
    print("=" * 118)
    for arm, exp, obs, ok in table:
        print(f"  [{'PASS' if ok else 'FAIL'}] {arm:<{w}} | expected: {exp} "
              f"| observed: {obs}")
    n = sum(1 for *_, ok in table if not ok)
    print("-" * 118)
    print(f"VERDICT: {'PASS' if n == 0 else 'FAIL'}   ({n} arm(s) failed of "
          f"{len(table)})")
    return 0 if n == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
