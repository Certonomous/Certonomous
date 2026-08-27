#!/usr/bin/env python3
"""Reconcile the DERIVED machine-readable TSV against the prose ANSYS register.

Prose register is the SOURCE OF TRUTH (append-only, CLAUDE.md rule 6); the TSV is derived.
This script re-derives independently and REFUSES (exit non-zero, with a NAMED message) on drift.

Checks (each drivable by --selftest):
  1 contiguity     TSV row ids are 1..N, no gaps, no duplicates
  2 rowcount       #TSV data rows == #prose register row-lines
  3 vocabulary     every TSV verdict is in the fixed vocabulary, nothing else
  4 verdict_match  per-row TSV verdict == verdict re-derived from prose (first-bolded-code-field rule)
  5 credentials    PASS set printed with ids; count == TSV header credentials_pass_count; ids == header
  6 append_only    sha256 of prose register row-lines 1..N == TSV header rows_1_to_N_sha256
                   (byte-integrity of every committed row the TSV knows: any edit to a committed
                    row above the last changes the hash and REFUSES. Rule 6 requires a dated
                    amendment for legitimate changes; a pure append leaves rows 1..N untouched and
                    is caught instead by check 2 as a stale-TSV rowcount mismatch.)

NO `assert` is used anywhere: `python3 -O` strips asserts, which would silently disable a guard
(L-357: a non-zero exit is not evidence a guard fired; only its refusal message is). Every guard
raises/returns an explicit named refusal.

Reads the prose register from `git show HEAD:<path>` by default (the worktree lags HEAD in this
lab, L-350). Override with --register FILE and --tsv FILE (used by --selftest with temp files).
"""
import re, sys, subprocess, hashlib

REG_PATH = "verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md"
TSV_PATH = "verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.tsv"
VOCAB = ["PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"]
ROW = re.compile(r'^\| \*\*([0-9]+)\*\* \|')
VER = re.compile(r'^\*\*`(' + "|".join(re.escape(v) for v in VOCAB) + r')`\*\*')

def split_fields(line):
    return re.split(r'(?<!\\)\|', line)

def prose_rows(text):
    """Return list of (row_id:int, verdict:str|None, rowline:str) for each register row-line."""
    out = []
    for l in text.split("\n"):
        m = ROW.match(l)
        if not m:
            continue
        verdict = None
        for fld in split_fields(l):
            vm = VER.match(fld.strip())
            if vm:
                verdict = vm.group(1)
                break
        out.append((int(m.group(1)), verdict, l))
    return out

def rows_hash(rowlines):
    h = hashlib.sha256()
    h.update("\n".join(rowlines).encode("utf-8"))
    return h.hexdigest()

def parse_tsv(text):
    meta = {}
    data = []
    header_cols = None
    for line in text.split("\n"):
        if not line.strip():
            continue
        if line.startswith("# meta:"):
            body = line[len("# meta:"):].strip()
            if "=" in body:
                k, v = body.split("=", 1)
                meta[k.strip()] = v.strip()
            continue
        if line.startswith("#"):
            continue
        if header_cols is None:
            header_cols = line.split("\t")
            continue
        data.append(dict(zip(header_cols, line.split("\t"))))
    return meta, header_cols, data

def validate(reg_text, tsv_text):
    """Run all six checks. Return (ok:bool, lines:list[str]). Never raises for a check failure;
    raises only on a malformed TSV header it cannot even parse (a distinct named refusal)."""
    lines = []
    ok = True
    meta, cols, data = parse_tsv(tsv_text)
    pr = prose_rows(reg_text)

    # ---- check 1: contiguity ----
    ids = []
    bad = False
    for d in data:
        try:
            ids.append(int(d["row_id"]))
        except (KeyError, ValueError):
            bad = True
    if bad or ids != list(range(1, len(ids) + 1)):
        ok = False
        lines.append(f"REFUSE[check1:contiguity]: TSV row ids are not contiguous 1..N: {ids}")
    else:
        lines.append(f"OK[check1:contiguity]: row ids 1..{len(ids)} contiguous, no gaps/dupes")

    # ---- check 2: rowcount ----
    if len(data) != len(pr):
        ok = False
        lines.append(f"REFUSE[check2:rowcount]: TSV has {len(data)} data rows but prose register "
                     f"has {len(pr)} row-lines (stale TSV or rows appended/removed)")
    else:
        lines.append(f"OK[check2:rowcount]: TSV rows {len(data)} == prose register row-lines {len(pr)}")

    # ---- check 3: vocabulary ----
    v3 = True
    for d in data:
        if d.get("verdict") not in VOCAB:
            ok = False; v3 = False
            lines.append(f"REFUSE[check3:vocabulary]: verdict {d.get('verdict')!r} at TSV row "
                         f"{d.get('row_id')} is not in the fixed vocabulary {VOCAB}")
    if v3:
        lines.append("OK[check3:vocabulary]: every TSV verdict is in the fixed vocabulary")

    # ---- check 4: verdict_match (independent re-derivation from prose) ----
    prose_by_id = {rid: verdict for rid, verdict, _ in pr}
    v4 = True
    for d in data:
        try:
            rid = int(d["row_id"])
        except (KeyError, ValueError):
            continue
        derived = prose_by_id.get(rid, "<no such prose row>")
        if d.get("verdict") != derived:
            ok = False; v4 = False
            lines.append(f"REFUSE[check4:verdict_match]: row {rid} TSV verdict {d.get('verdict')!r} "
                         f"!= prose-derived {derived!r}")
    if v4:
        lines.append("OK[check4:verdict_match]: every TSV verdict matches the prose re-derivation")

    # ---- check 5: credentials ----
    derived_creds = sorted(int(d["row_id"]) for d in data if d.get("verdict") == "PASS")
    hdr_count = meta.get("credentials_pass_count")
    hdr_ids = meta.get("credential_row_ids", "")
    hdr_ids_list = sorted(int(x) for x in hdr_ids.split(",") if x.strip()) if hdr_ids.strip() else []
    lines.append(f"CREDENTIALS (PASS rows): count={len(derived_creds)} ids={derived_creds}")
    c5 = True
    if hdr_count is None or int(hdr_count) != len(derived_creds):
        ok = False; c5 = False
        lines.append(f"REFUSE[check5:credentials]: header credentials_pass_count={hdr_count} but "
                     f"{len(derived_creds)} PASS rows derived — silent credential drift")
    if hdr_ids_list != derived_creds:
        ok = False; c5 = False
        lines.append(f"REFUSE[check5:credentials]: header credential_row_ids={hdr_ids_list} but "
                     f"derived PASS ids={derived_creds}")
    if c5:
        lines.append(f"OK[check5:credentials]: {len(derived_creds)} credentials {derived_creds} "
                     f"match TSV header")

    # ---- check 6: append_only (byte integrity of committed rows) ----
    n = len(data)
    hdr_hash = meta.get("rows_1_to_N_sha256")
    if len(pr) < n:
        ok = False
        lines.append(f"REFUSE[check6:append_only]: prose register has only {len(pr)} row-lines, "
                     f"fewer than the TSV's {n} — a committed row was removed (rule 6 violation)")
    else:
        got = rows_hash([rowline for _, _, rowline in pr[:n]])
        if hdr_hash is None or got != hdr_hash:
            ok = False
            lines.append(f"REFUSE[check6:append_only]: sha256 of prose register rows 1..{n} = {got} "
                         f"!= TSV header rows_1_to_N_sha256 = {hdr_hash} — a committed row was "
                         f"modified above the last without a dated amendment (rule 6)")
        else:
            lines.append(f"OK[check6:append_only]: prose register rows 1..{n} byte-hash matches TSV header")

    if ok:
        lines.append(f"PASS: ANSYS register TSV reconciled with prose register — {len(data)} rows, "
                     f"credentials {derived_creds} count {len(derived_creds)}, all 6 checks OK")
    else:
        lines.append("REFUSE: ANSYS register TSV FAILED reconciliation — see the check line(s) above")
    return ok, lines

def read_register(args):
    if "--register" in args:
        p = args[args.index("--register") + 1]
        return open(p, encoding="utf-8").read()
    return subprocess.run(["git", "show", f"HEAD:{REG_PATH}"],
                          capture_output=True, text=True, check=True).stdout

def read_tsv(args):
    if "--tsv" in args:
        p = args[args.index("--tsv") + 1]
        return open(p, encoding="utf-8").read()
    return open(TSV_PATH, encoding="utf-8").read()

# ------------------------- selftest -------------------------
def _mut_tsv_meta(tsv, key, newval):
    out = []
    for l in tsv.split("\n"):
        if l.startswith(f"# meta: {key}="):
            out.append(f"# meta: {key}={newval}")
        else:
            out.append(l)
    return "\n".join(out)

def _mut_tsv_first_verdict(tsv, newv):
    out = []
    done = False
    for l in tsv.split("\n"):
        if not done and l and not l.startswith("#") and "\t" in l and l.split("\t")[0].isdigit():
            f = l.split("\t"); f[3] = newv; l = "\t".join(f); done = True
        out.append(l)
    return "\n".join(out)

def _drop_last_tsv_row(tsv):
    lines = tsv.split("\n")
    idx = max(i for i, l in enumerate(lines) if l and not l.startswith("#") and "\t" in l and l.split("\t")[0].isdigit())
    return "\n".join(lines[:idx] + lines[idx + 1:])

def _mut_tsv_rowid(tsv, oldid, newid):
    out = []
    for l in tsv.split("\n"):
        if l and not l.startswith("#") and "\t" in l:
            f = l.split("\t")
            if f[0] == oldid:
                f[0] = newid; l = "\t".join(f)
        out.append(l)
    return "\n".join(out)

def _mut_reg_early_row_prose(reg):
    # change a NON-verdict byte in an early register row (row 1 case description)
    out = []
    done = False
    for l in reg.split("\n"):
        if not done and ROW.match(l):
            l = l.replace("Flow", "FLOW_PLANTED", 1)  # a word in the case column, not the verdict
            done = True
        out.append(l)
    return "\n".join(out)

def selftest(args=None):
    args = args or []
    reg = read_register(args)        # prose register (HEAD, or --register)
    tsv = read_tsv(args)             # derived TSV (TSV_PATH, or --tsv)
    arms = []
    # clean control
    ok, ls = validate(reg, tsv)
    txt = "\n".join(ls)
    arms.append(("CLEAN control -> PASS",
                 ok and "PASS: ANSYS register TSV reconciled" in txt))
    # check 1: introduce a duplicate/gap in ids
    bad1 = _mut_tsv_rowid(tsv, "2", "3")
    ok, ls = validate(reg, bad1); txt = "\n".join(ls)
    arms.append(("check1 contiguity -> REFUSE[check1:contiguity]",
                 (not ok) and "REFUSE[check1:contiguity]:" in txt))
    # check 2: drop a TSV row (rowcount mismatch) — but keep ids contiguous by dropping the LAST
    bad2 = _drop_last_tsv_row(tsv)
    ok, ls = validate(reg, bad2); txt = "\n".join(ls)
    arms.append(("check2 rowcount -> REFUSE[check2:rowcount]",
                 (not ok) and "REFUSE[check2:rowcount]:" in txt))
    # check 3: verdict not in vocab
    bad3 = _mut_tsv_first_verdict(tsv, "FAIL")
    ok, ls = validate(reg, bad3); txt = "\n".join(ls)
    arms.append(("check3 vocabulary -> REFUSE[check3:vocabulary]",
                 (not ok) and "REFUSE[check3:vocabulary]:" in txt))
    # check 4: verdict in vocab but != prose derivation (row 1 is NOT A RESULT; set to PENDING)
    bad4 = _mut_tsv_first_verdict(tsv, "PENDING")
    ok, ls = validate(reg, bad4); txt = "\n".join(ls)
    arms.append(("check4 verdict_match -> REFUSE[check4:verdict_match]",
                 (not ok) and "REFUSE[check4:verdict_match]:" in txt))
    # check 5: corrupt the header credential count
    bad5 = _mut_tsv_meta(tsv, "credentials_pass_count", "99")
    ok, ls = validate(reg, bad5); txt = "\n".join(ls)
    arms.append(("check5 credentials -> REFUSE[check5:credentials]",
                 (not ok) and "REFUSE[check5:credentials]:" in txt))
    # check 6: modify a committed prose row above the last (non-verdict byte)
    bad6reg = _mut_reg_early_row_prose(reg)
    ok, ls = validate(bad6reg, tsv); txt = "\n".join(ls)
    arms.append(("check6 append_only -> REFUSE[check6:append_only]",
                 (not ok) and "REFUSE[check6:append_only]:" in txt))
    npass = sum(1 for _, good in arms if good)
    print(f"SELFTEST arms {npass}/{len(arms)}:")
    for name, good in arms:
        print(f"  [{'PASS' if good else 'FAIL'}] {name}")
    if npass != len(arms):
        print("SELFTEST FAILED: not every arm behaved as expected")
        return 1
    print(f"SELFTEST OK: {npass}/{len(arms)} arms — each check driven to its named refusal, "
          f"clean control passes")
    return 0

def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        raise SystemExit(selftest(args))
    reg = read_register(args)
    tsv = read_tsv(args)
    ok, ls = validate(reg, tsv)
    for l in ls:
        print(l)
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
