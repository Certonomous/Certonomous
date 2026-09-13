#!/usr/bin/env python3
"""
D6R3 RULE-17 GATE -- GATE ON THE MESH THE SOLVER READ, NEVER THE MESH YOU GENERATED.

DRAFT.  Registered by PREREGISTRATION.md (R4) section 8d.  Launches no compute.
Nothing here is sent, filed or submitted (CLAUDE.md rule 7).

WHY THIS FILE EXISTS, and it is the clause the supervisor calls "the one that would have caught
the most":  FM8 was graded a FRESH-MESH CONFIRMATION and the retraction found
**1,486 processor meshes scanned, zero matching the freshly extruded mesh -- no arm had ever
loaded it.**  Staging the mesh into every processor case is the ARM.  Hashing what the ranks
ACTUALLY READ is the GATE.  A registered clause that does not execute is not a gate, and after a
freeze sha it can only become an addendum -- and an addendum cannot add a gate.

WHAT IT DOES.  Before run_model(), for each condition, it rebuilds the global point set from every
rank's own `constant/polyMesh/points` and `constant/polyMesh/pointProcAddressing`, and compares the
reconstruction for EXACT EQUALITY against the mesh this arm generated.

EXACT EQUALITY, NO TOLERANCE.  The comparison is `reconstructed == generated` on the parsed values
and on their canonical bytes.  A tolerance here would silently re-admit exactly the class of defect
the gate exists for: a mesh that is *nearly* the one we generated is a mesh we did not generate.
`CONTROL_SOURCE_HAS_NO_TOLERANCE` in the selftest asserts on THIS FILE'S OWN SOURCE TEXT that no
tolerance has been introduced, so a future edit that adds one fails there.
"""
import argparse, gzip, hashlib, json, os, re, sys

VERSION = "D6R3-MESHREADGATE-DRAFT-1"


class Refusal(Exception):
    pass


def _open(path):
    if os.path.isfile(path):
        return open(path, "rb")
    if os.path.isfile(path + ".gz"):
        return gzip.open(path + ".gz", "rb")
    raise Refusal("not readable: %s (nor .gz)" % path)


_NUM = re.compile(rb"[-+0-9.eE]+")


def read_points(path):
    """Parse an OpenFOAM ascii pointField into a list of (x, y, z) strings, kept as the file's own
    text so the comparison is on the bytes the solver read, not on a re-formatted float."""
    with _open(path) as f:
        raw = f.read()
    body = raw.split(b"(", 1)
    if len(body) < 2:
        raise Refusal("no list body in %s" % path)
    m = re.search(rb"\n(\d+)\s*\n\(", raw)
    if not m:
        raise Refusal("no count header in %s -- binary format is not parsed by this reader" % path)
    n = int(m.group(1))
    start = m.end()
    out = []
    for mm in re.finditer(rb"\(([^)]*)\)", raw[start:]):
        parts = mm.group(1).split()
        if len(parts) != 3:
            continue
        out.append((parts[0].decode(), parts[1].decode(), parts[2].decode()))
        if len(out) == n:
            break
    if len(out) != n:
        raise Refusal("%s: header says %d points, parsed %d" % (path, n, len(out)))
    return out


def read_labels(path):
    """Parse an OpenFOAM ascii labelList (pointProcAddressing)."""
    with _open(path) as f:
        raw = f.read()
    m = re.search(rb"\n(\d+)\s*\n\(", raw)
    if not m:
        raise Refusal("no count header in %s" % path)
    n = int(m.group(1))
    start = m.end()
    end = raw.find(b")", start)
    vals = [int(x) for x in raw[start:end].split()]
    if len(vals) != n:
        raise Refusal("%s: header says %d labels, parsed %d" % (path, n, len(vals)))
    return vals


def canonical_hash(points):
    h = hashlib.md5()
    for p in points:
        h.update(("%s %s %s\n" % p).encode())
    return h.hexdigest()


def reconstruct_from_ranks(case_dir):
    """Rebuild the global point set from what each rank ACTUALLY holds."""
    try:
        entries = os.listdir(case_dir)
    except OSError as e:
        # REFUSE, never traceback.  An unhandled exception is not a refusal: it exits on a code
        # this registration did not register, and a reader cannot tell it from a crash.
        raise Refusal("case directory not readable: %s (%s)" % (case_dir, e.__class__.__name__))
    procs = sorted(d for d in entries
                   if d.startswith("processor") and d[len("processor"):].isdigit())
    if not procs:
        raise Refusal("no processor* directories under %s -- nothing was decomposed, so nothing "
                      "can be shown to have been read" % case_dir)
    glob = {}
    per_rank = {}
    for d in procs:
        pm = os.path.join(case_dir, d, "constant", "polyMesh")
        pts = read_points(os.path.join(pm, "points"))
        addr_path = os.path.join(pm, "pointProcAddressing")
        if not (os.path.isfile(addr_path) or os.path.isfile(addr_path + ".gz")):
            raise Refusal("%s has no pointProcAddressing -- the reconstruction that proves what "
                          "this rank read is not possible" % d)
        addr = read_labels(addr_path)
        if len(addr) != len(pts):
            raise Refusal("%s: %d points but %d addressing entries" % (d, len(pts), len(addr)))
        per_rank[d] = len(pts)
        for i, g in enumerate(addr):
            if g in glob and glob[g] != pts[i]:
                raise Refusal("%s: global point %d is claimed twice with DIFFERENT values -- the "
                              "ranks did not read one mesh" % (d, g))
            glob[g] = pts[i]
    n = max(glob) + 1
    if len(glob) != n:
        raise Refusal("the ranks' addressing covers %d of %d global points -- the reconstruction "
                      "is incomplete and a partial reconstruction is not evidence" % (len(glob), n))
    return [glob[i] for i in range(n)], per_rank


def gate(case_dir, generated_points_path):
    """RULE 17.  Returns OK only when the reconstruction EXACTLY equals the generated mesh."""
    recon, per_rank = reconstruct_from_ranks(case_dir)
    generated = read_points(generated_points_path)
    h_recon = canonical_hash(recon)
    h_gen = canonical_hash(generated)
    # EXACT EQUALITY.  No tolerance, on the values and on their canonical bytes.
    same_len = len(recon) == len(generated)
    values_equal = same_len and recon == generated
    bytes_equal = h_recon == h_gen
    ok = values_equal and bytes_equal
    res = {"gate": "R17_MESH_READ", "verdict": "OK" if ok else "REFUSE",
           "n_ranks": len(per_rank), "points_per_rank": per_rank,
           "n_points_reconstructed": len(recon), "n_points_generated": len(generated),
           "hash_reconstructed": h_recon, "hash_generated": h_gen,
           "comparison": "EXACT EQUALITY, no tolerance",
           "derived_from": "PREREGISTRATION R4 section 8d; standing rule 17"}
    if not ok:
        res["why"] = ("the mesh the ranks READ is not the mesh this arm GENERATED"
                      if same_len else
                      "point counts differ: read %d, generated %d" % (len(recon), len(generated)))
    return res


# ==============================================================================================
# CONTROLS.  Driven against a KNOWN-BAD input and required to REFUSE.
# ==============================================================================================

def _hdr(kind, n, body):
    return ("FoamFile\n{ version 2.0; format ascii; class %s; object x; }\n\n%d\n(\n%s\n)\n"
            % (kind, n, body)).encode()


def _write_case(root, ranks, gen_points):
    os.makedirs(root, exist_ok=True)
    for r, (idx, pts) in enumerate(ranks):
        pm = os.path.join(root, "processor%d" % r, "constant", "polyMesh")
        os.makedirs(pm, exist_ok=True)
        open(os.path.join(pm, "points"), "wb").write(
            _hdr("vectorField", len(pts), "\n".join("(%s %s %s)" % p for p in pts)))
        open(os.path.join(pm, "pointProcAddressing"), "wb").write(
            _hdr("labelList", len(idx), " ".join(str(i) for i in idx)))
    gp = os.path.join(root, "generated_points")
    open(gp, "wb").write(_hdr("vectorField", len(gen_points),
                              "\n".join("(%s %s %s)" % p for p in gen_points)))
    return gp


def selftest(verbose=True):
    import shutil, tempfile
    res = []

    def c(name, fn, want):
        try:
            got = fn()
        except Refusal as e:
            got = "REFUSE"
            name += "  [%s]" % str(e)[:60]
        return {"control": name, "want": want, "got": got, "PASS": got == want}

    tmp = tempfile.mkdtemp(prefix="d6r3_r17_")
    try:
        GEN = [("%.12g" % (i * 1.5), "%.12g" % (i * 2.5), "%.12g" % (i * 3.5)) for i in range(10)]
        BASE = [("%.12g" % (i * 1.5 + 0.001), "%.12g" % (i * 2.5), "%.12g" % (i * 3.5))
                for i in range(10)]

        d = os.path.join(tmp, "clean")
        gp = _write_case(d, [([0, 1, 2, 3, 4], GEN[:5]), ([5, 6, 7, 8, 9], GEN[5:])], GEN)
        res.append(c("R17.clean -- two ranks whose union reconstructs the generated mesh exactly",
                     lambda: gate(d, gp)["verdict"], "OK"))

        d2 = os.path.join(tmp, "baserank")
        gp2 = _write_case(d2, [([0, 1, 2, 3, 4], BASE[:5]), ([5, 6, 7, 8, 9], GEN[5:])], GEN)
        res.append(c("R17.KNOWN-BAD -- ONE RANK HOLDS THE BASE MESH, NOT THE STAGED ONE: this is "
                     "the FM8 class, 1,486 processor meshes that matched nothing",
                     lambda: gate(d2, gp2)["verdict"], "REFUSE"))

        d3 = os.path.join(tmp, "oneulp")
        one = list(GEN)
        one[7] = ("%.17g" % (7 * 1.5 + 1e-15), one[7][1], one[7][2])
        gp3 = _write_case(d3, [([0, 1, 2, 3, 4], one[:5]), ([5, 6, 7, 8, 9], one[5:])], GEN)
        res.append(c("R17.KNOWN-BAD -- a SINGLE point differing in its last digits: EXACT equality "
                     "must refuse where a tolerance would not",
                     lambda: gate(d3, gp3)["verdict"], "REFUSE"))

        d4 = os.path.join(tmp, "noprocs"); os.makedirs(d4, exist_ok=True)
        gp4 = os.path.join(d4, "generated_points")
        open(gp4, "wb").write(_hdr("vectorField", len(GEN),
                                   "\n".join("(%s %s %s)" % p for p in GEN)))
        res.append(c("R17.BLIND -- no processor* directories: nothing can be shown to have been read",
                     lambda: gate(d4, gp4)["verdict"], "REFUSE"))

        d5 = os.path.join(tmp, "noaddr")
        gp5 = _write_case(d5, [([0, 1, 2, 3, 4], GEN[:5]), ([5, 6, 7, 8, 9], GEN[5:])], GEN)
        os.remove(os.path.join(d5, "processor1", "constant", "polyMesh", "pointProcAddressing"))
        res.append(c("R17.BLIND -- a rank with no pointProcAddressing: the reconstruction that "
                     "proves what it read is impossible",
                     lambda: gate(d5, gp5)["verdict"], "REFUSE"))

        d6 = os.path.join(tmp, "partial")
        gp6 = _write_case(d6, [([0, 1, 2, 3, 4], GEN[:5]), ([5, 6, 7, 9, 9], GEN[5:])], GEN)
        res.append(c("R17.BLIND -- addressing that does not cover every global point: a PARTIAL "
                     "reconstruction is not evidence",
                     lambda: gate(d6, gp6)["verdict"], "REFUSE"))

        d7 = os.path.join(tmp, "shortgen")
        gp7 = _write_case(d7, [([0, 1, 2, 3, 4], GEN[:5]), ([5, 6, 7, 8, 9], GEN[5:])], GEN[:9])
        res.append(c("R17.KNOWN-BAD -- the generated mesh has a different point count",
                     lambda: gate(d7, gp7)["verdict"], "REFUSE"))

        # THE SOURCE-TEXT CONTROL: a future edit that introduces a tolerance must FAIL HERE.
        # It scans EXECUTABLE CODE ONLY -- comments and docstrings are stripped with tokenize,
        # because a tolerance written in prose is not a tolerance and a control that cannot tell
        # the difference is a control that will be silenced rather than obeyed.  (This control
        # DID fire on its first run, on the word "tolerance" in gate()'s own docstring; the
        # control was made precise, the gate was not made loose -- PREREGISTRATION R4 s8d.)
        import io, tokenize as _tk
        src = open(os.path.abspath(__file__)).read()
        fn_src = src[src.index("def gate("):src.index("# ====", src.index("def gate("))]
        code = []
        for tok in _tk.generate_tokens(io.StringIO(fn_src).readline):
            if tok.type in (_tk.COMMENT, _tk.STRING, _tk.NL, _tk.NEWLINE, _tk.INDENT, _tk.DEDENT):
                continue
            code.append(tok.string)
        code = " ".join(code)
        banned = ("tol", "atol", "rtol", "isclose", "allclose", "abs", "round", "delta", "eps")
        found = [b for b in banned if b in code]
        res.append({"control": "R17.CONTROL_SOURCE_HAS_NO_TOLERANCE -- gate()'s own source text "
                               "contains no tolerance construct (%s)" % ", ".join(banned),
                    "want": [], "got": found, "PASS": found == []})
        # PLANTED CONTROL (rule 3): the scan is shown able to SEE a tolerance before its zero is
        # believed.  A reader not shown able to see a non-zero is not a reader.
        mutated = fn_src.replace("values_equal = same_len and recon == generated",
                                 "values_equal = same_len and math.isclose(1, 1, rel_tol=1e-9)")
        mcode = []
        for tok in _tk.generate_tokens(io.StringIO(mutated).readline):
            if tok.type in (_tk.COMMENT, _tk.STRING, _tk.NL, _tk.NEWLINE, _tk.INDENT, _tk.DEDENT):
                continue
            mcode.append(tok.string)
        mfound = [b for b in banned if b in " ".join(mcode)]
        res.append({"control": "R17.CONTROL_IS_LIVE -- the same scan over a MUTATED gate() that "
                               "compares with math.isclose(rel_tol=...) must FIND the tolerance, "
                               "or its zero on the real source is not evidence (rule 3)",
                    "want": True, "got": mfound != [], "PASS": mfound != []})
        res.append({"control": "R17.CONTROL_SOURCE_IS_EXACT -- gate() compares with == on both "
                               "the values and the canonical bytes",
                    "want": True,
                    "got": ("recon == generated" in fn_src and "h_recon == h_gen" in fn_src),
                    "PASS": ("recon == generated" in fn_src and "h_recon == h_gen" in fn_src)})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_pass = sum(1 for x in res if x["PASS"]); n_fail = len(res) - n_pass
    assert n_pass + n_fail == len(res)
    if verbose:
        for x in res:
            print("%-6s want=%-8r got=%-8r %s" % ("PASS" if x["PASS"] else "FAIL",
                                                  x["want"], x["got"], x["control"]))
        print("\nD6R3_R17 SELFTEST  n_total=%d  n_pass=%d  n_fail=%d" % (len(res), n_pass, n_fail))
        print("D6R3_R17 SELFTEST %s" % ("PASS" if n_fail == 0 else "FAIL"))
    return res, n_pass, n_fail


def main(argv=None):
    ap = argparse.ArgumentParser(prog="d6r3_mesh_read_gate.py")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--case", default=None, help="condition run directory holding processor*")
    ap.add_argument("--generated", default=None, help="the points file this arm generated")
    ap.add_argument("--json", default=None)
    ap.add_argument("--version", action="store_true")
    a = ap.parse_args(argv)
    if a.version:
        print(VERSION); return 0
    if a.selftest:
        r, np_, nf = selftest()
        if a.json:
            json.dump({"version": VERSION, "n_total": len(r), "n_pass": np_, "n_fail": nf,
                       "controls": r}, open(a.json, "w"), indent=1, default=str)
            print("wrote %s" % a.json)
        return 0 if nf == 0 else 1
    if not (a.case and a.generated):
        ap.print_help(); return 64
    try:
        out = gate(a.case, a.generated)
    except Refusal as e:
        out = {"gate": "R17_MESH_READ", "verdict": "REFUSE", "why": str(e)}
    except Exception as e:  # refuse rather than degrade, and never on an unregistered exit code
        out = {"gate": "R17_MESH_READ", "verdict": "REFUSE",
               "why": "unexpected %s: %s" % (e.__class__.__name__, e)}
    print(json.dumps(out, indent=1))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    return 0 if out["verdict"] == "OK" else 2


if __name__ == "__main__":
    sys.exit(main())
