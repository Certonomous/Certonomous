#!/usr/bin/env python3
"""SO-1bR GRADER ENTRY POINT -- the `--root/--out` command line the chain driver
invokes at chain end.  IT DECIDES NOTHING.

WHY THIS IS A SEPARATE FILE AND NOT A FEW LINES ADDED TO `so1br_grade.py`.
`so1br_grade.py` was FROZEN at Stage 1 (commit `5774967c`), its md5 is registered
in PREREGISTRATION.md section 9, and the supervisor discharged check 1 by reading
those exact bytes.  Standing rule 6: a frozen file is never edited.  Adding a CLI
to it would silently invalidate both the registered md5 and the reading that
cleared it, so the CLI is added BESIDE it instead and the frozen instrument stays
byte-identical.  That is the whole reason this file exists; it holds no gate, no
band, no threshold and no composition rule.

WHAT IT DOES, IN ORDER:
  1. asserts `so1br_grade.py` on disk is the Stage-1 frozen file, BY MD5;
  2. imports it and calls its `grade_root()`, which copies the run root, takes
     md5 manifests before and after, adopts the frozen `so1b_grade.py`, audits
     the rebind, runs the FROZEN `grade()`, and emits through
     `require_travelling_provenance()`;
  3. writes the returned object as JSON.

ON THE REFUSAL PATH, AND IT IS THE PART WORTH READING.  If `grade_root()` refuses
-- an absent root, a mutated preserved root, a rebind that is not the registered
one, a precondition that no longer proceeds -- there is no graded object to write.
A refusal still produces a VERDICT (`NOT A RESULT`), and G-PROV says no verdict
leaves this item without its upstream provenance.  So this file re-derives the
provenance INDEPENDENTLY and puts the refusal record through the SAME
`require_travelling_provenance()` gate.  If THAT fails too -- if the upstream
artefact is itself unreadable -- the record written carries NO `verdict` field at
all and says so in `verdict_withheld_reason`.  A refusal that cannot carry its
provenance is not given a verdict word rather than being given one quietly.

L-332: NO `assert` anywhere; the module counts `ast.Assert` nodes in its own
source and refuses on any, so `python3 -O` cannot strip a check.
"""

import sys

# ABOVE ANY OTHER IMPORT.  A stale `.pyc` inverts mutation tests and
# `PYTHONDONTWRITEBYTECODE` does not cure it.
sys.dont_write_bytecode = True

import argparse         # noqa: E402
import ast              # noqa: E402
import hashlib          # noqa: E402
import importlib.util   # noqa: E402
import json             # noqa: E402
import os               # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# The Stage-1 frozen instrument, pinned by the md5 registered in
# PREREGISTRATION.md section 9 and cleared by the supervisor's own check 1.
FROZEN_STAGE1 = os.path.join(HERE, "so1br_grade.py")
FROZEN_STAGE1_MD5 = "9736ca91c9c111877f86dc048b38e929"
PRECONDITION = os.path.join(HERE, "so1br_precondition.py")
PRECONDITION_MD5 = "447eaada4a896fc5f8b0f4ced4cb2af8"


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail},
                             sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read()))
               if isinstance(n, ast.Assert))


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(path, md5_expected, name):
    if not os.path.isfile(path):
        refuse("FROZEN_INSTRUMENT_ABSENT", {"path": path})
    got = md5_file(path)
    if got != md5_expected:
        refuse("FROZEN_INSTRUMENT_MD5", {"path": path, "registered": md5_expected,
                                         "on_disk": got,
                                         "note": "rule 6: a frozen file is never edited, "
                                                 "and this one carries the supervisor's "
                                                 "own check-1 reading"})
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--tmpdir", default=None)
    args = ap.parse_args(argv)

    na = count_asserts(os.path.abspath(__file__))
    if na != 0:
        sys.stderr.write("REFUSE this file carries %d ast.Assert nodes (L-332)\n" % na)
        return 2
    if not args.root:
        sys.stderr.write("usage: so1br_grade_cli.py --root <run root> [--out FILE]\n")
        return 64

    record = {"item": "CURRICULUM-SO1bR", "root": args.root,
              "entry_point": os.path.abspath(__file__),
              "frozen_stage1": FROZEN_STAGE1, "frozen_stage1_md5": FROZEN_STAGE1_MD5}
    rc = 0
    try:
        G = load_module(FROZEN_STAGE1, FROZEN_STAGE1_MD5, "so1br_stage1")
        P = load_module(PRECONDITION, PRECONDITION_MD5, "so1br_precond_cli")
        record["precondition_md5"] = PRECONDITION_MD5
        out = G.grade_root(args.root, workdir=args.tmpdir)
        record.update(out)
    except Exception as ex:                                           # noqa: BLE001
        if type(ex).__name__ != "Refusal":
            raise
        # A REFUSAL STILL PRODUCES A VERDICT, so it still owes its provenance.
        record["refusal"] = str(ex)
        rc = 2
        try:
            P = load_module(PRECONDITION, PRECONDITION_MD5, "so1br_precond_refusal")
            G2, src = P.read_registered_input()
            prov = P.shipped_provenance(G2, os.path.basename(src["path"]))
            record["verdict"] = "NOT A RESULT"
            record["upstream_provenance"] = prov
            record["verdict_line"] = P.compose_verdict_line("NOT A RESULT", prov)
            P.require_travelling_provenance(record)
        except Exception as ex2:                                      # noqa: BLE001
            record.pop("verdict", None)
            record.pop("verdict_line", None)
            record.pop("upstream_provenance", None)
            record["verdict_withheld_reason"] = (
                "the refusal record could not carry its upstream provenance, so NO "
                "verdict word is written rather than one written without it (G-PROV). "
                "underlying: %s" % (str(ex2)[:400],))
            rc = 3

    text = json.dumps(record, sort_keys=True, indent=2, default=str)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
        print("WROTE %s" % args.out)
    else:
        print(text)
    print("verdict=%s verdict_line_present=%s"
          % (record.get("verdict", "WITHHELD"), "verdict_line" in record))
    return rc


if __name__ == "__main__":
    sys.exit(main())
