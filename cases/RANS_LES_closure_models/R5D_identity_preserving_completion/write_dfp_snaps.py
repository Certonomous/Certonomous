#!/usr/bin/env python3
"""R5D dfpSnaps writer - the run-side producer of the G-DFP snapshot sequence.

STATUS: **UNFROZEN**.  This file is a RUN-SIDE PRODUCER, not a measurement
instrument.  It is NOT part of R5D's frozen grading path and it is NOT sha-pinned
by PREREGISTRATION.md sec.7.  Freezing (or declining to freeze) it is the
closure-supervisor's SUPERVISION_CHARTER sec.3 check-1/check-4 act, not this
file's claim.  Nothing here edits, imports-and-mutates, or shadows any frozen
file: `grade_r5d.py` and `PREREGISTRATION.md` are read only, and the frozen
comparator's sha256 is verified against the sec.7 pin before this writer will
run at all.

WHAT IT DOES
------------
`grade_r5d.py:load_snapshots` (frozen, line 248) reads the per-iteration
snapshot sequence from

    <case_dir>/dfpSnaps/<field>_<iter>

ascending in <iter>, and `distance_to_fixed_point` (frozen, line 162) turns that
sequence into the G-DFP distance.  Nothing in the lab wrote that directory, so
`load_snapshots` returns None on every case that exists today and the DFP
measurement is honestly PENDING.  This writer closes that gap.

MECHANISM-AGNOSTIC BY CONSTRUCTION
----------------------------------
PREREGISTRATION.md item 1 (lines 103-115) registers TWO acceptable mechanisms
for OBTAINING the iterates:

  (A) the driver writes the last DFP_KMIN+2 consecutive outer-iteration fields
      during the R5D run; or
  (B) if R5D reuses the R5C driver unchanged, the sequence is produced by
      re-solving from the written field and capturing the last 5 iterates,

both "provided the snapshots are consecutive outer iterates ending at the write
iteration".

This writer implements NEITHER capture front-end and CHOOSES NEITHER.  It is the
back-end both mechanisms share: given consecutive outer iterates already on disk
(as OpenFOAM time directories, or as an explicit iter=path list), it normalises
them into the frozen reader's layout, enforces the registered proviso
(consecutive, ending at a caller-named iteration, at least DFP_KMIN+2 of them),
and PROVES the frozen reader can consume the result before it returns.  Which
mechanism supplies the iterates is the supervisor's call.

FORMAT AUTHORITY IS THE FROZEN READER, NOT THE PROSE
----------------------------------------------------
`of_read.read_field` tries `Ofpp.parse_internal_field` first and falls back to
`of_read._read_headerless`.  **Ofpp is not installed on this box**, so the
effective parser today is `_read_headerless`, which requires, in order:
  1. a literal `nonuniform List<T>` marker with T in {scalar,vector,symmTensor,
     tensor}  (a `uniform` placeholder is UNREADABLE and is refused here);
  2. after that marker, `<count>` then `(`;
  3. the list terminated by `)` at the START of a line (the body is truncated at
     the first "\n)", which is what strips the trailing boundaryField block);
  4. exactly count*ncomp numbers in that body.
The primary write path is therefore a BYTE-FOR-BYTE COPY of the solver's own
field file: zero re-serialisation, zero precision loss, zero format risk, and
the boundaryField block is carried along and harmlessly truncated by the reader.
An array path exists for synthetic controls only and is labelled as such in the
file it writes.

CONTROLS (CLAUDE.md rule 3, L-235, L-332/D476 sec.31.3)
-------------------------------------------------------
No `assert` carries any guard, refusal, control or gate anywhere in this file -
asserts vanish under `python3 -O`.  Every refusal is an explicit branch into
`refuse()` -> sys.exit(2).  `--selftest` is green under BOTH `python3` and
`python3 -O`, plants a sequence whose d_rel is PREDICTED ANALYTICALLY and checks
the frozen reader returns that value, and shows the frozen reader's flat/clipped
and cliff REFUSALS actually FIRE.  A selftest that only ever passes is the weak
test.

Verdict vocabulary only (CLAUDE.md rule 1):
  PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
This writer asserts NO verdict.  It produces run-side data.
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_CLOSURE = os.path.join(_REPO, "cases", "RANS_LES_closure_models")
sys.path.insert(0, os.path.join(_CLOSURE, "_common"))

import of_read                                  # noqa: E402  (THE format authority)

# ---- the frozen grading path (READ ONLY, sha-verified before use) ------------
GRADER_PATH = os.path.join(_HERE, "grade_r5d.py")
PREREG_PATH = os.path.join(_HERE, "PREREGISTRATION.md")
# PREREGISTRATION.md sec.7 line 306 comparator sha-pin (CLAUDE.md rule 2: verify
# the frozen file IS the file that runs by hashing it).
GRADER_SHA_PIN = "aaae8ac6d60c8aa33124748e8410b094483ec48f67f54f289d0aff3af07e5805"

SNAPDIR = "dfpSnaps"
MANIFEST = "MANIFEST.json"          # does NOT match <field>_<digits>, so the
#                                     frozen load_snapshots regex ignores it.
_ITER_RE = re.compile(r"^(\d+)$")
_NCOMP_CLASS = {1: ("scalar", "volScalarField"),
                3: ("vector", "volVectorField"),
                6: ("symmTensor", "volSymmTensorField"),
                9: ("tensor", "volTensorField")}

# The R5D run root the frozen grader grades (grade_r5d.py:62).  The selftest may
# never write inside it.
R5D_RUN_ROOT = "/home/ubuntu/closure-data/r5d/frozen"
SELFTEST_ROOT = "/home/ubuntu/closure-data/r5d/writer_selftest"


# ------------------------------------------------------------------ utilities
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def refuse(msg):
    """Every guard, control and gate in this file ends here.  Never an assert."""
    print(f"\nWRITER REFUSAL: {msg}", file=sys.stderr)
    print("NOT A RESULT (no dfpSnaps sequence was certified)", file=sys.stderr)
    sys.exit(2)


def load_frozen_grader():
    """Import the FROZEN grader as a module, after verifying its sha-pin.

    The writer takes DFP_KMIN and the DFP constants FROM the frozen file rather
    than restating them, so the two can never drift apart.
    """
    if not os.path.exists(GRADER_PATH):
        refuse(f"frozen grader absent: {GRADER_PATH}")
    got = sha256_file(GRADER_PATH)
    if got != GRADER_SHA_PIN:
        refuse(f"frozen grader sha256 {got} != PREREGISTRATION.md sec.7 pin "
               f"{GRADER_SHA_PIN}: the grading path is not the frozen one "
               f"(CLAUDE.md rule 2)")
    spec = importlib.util.spec_from_file_location("_frozen_grade_r5d", GRADER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, got


def no_assert_in_this_file():
    """L-332 / D476 sec.31.3: an `assert` is stripped under `python3 -O`, so no
    guard may ride on one.  Counted by an independent parse of our own source."""
    with open(os.path.abspath(__file__), "r") as fh:
        tree = ast.parse(fh.read())
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))


# ------------------------------------------------- the reader's own dialect
def read_or_refuse(path, what):
    """Read a field THROUGH the frozen reader.  The reader is the authority on
    what it can read; a source it cannot parse is refused here, not at grading."""
    if not os.path.isfile(path):
        refuse(f"{what}: not a file: {path}")
    try:
        arr = np.asarray(of_read.read_field(path), dtype=float)
    except Exception as exc:                     # noqa: BLE001 - report anything
        refuse(f"{what}: the FROZEN reader (of_read.read_field) cannot parse "
               f"{path}: {type(exc).__name__}: {exc}.  A `uniform` placeholder "
               f"or a binary-format field is unreadable and must not be written "
               f"into {SNAPDIR}/")
    if arr.size == 0:
        refuse(f"{what}: {path} parsed to an EMPTY array")
    if not np.all(np.isfinite(arr)):
        refuse(f"{what}: {path} contains non-finite values (inf/nan)")
    return arr


def write_field_ascii(path, values, field, iteration, synthetic_note):
    """Emit ONE OpenFOAM ascii internal field in the dialect the frozen reader
    parses.  SYNTHETIC/CONTROL PATH ONLY - real snapshots are byte-copied.

    Shape (N,) or (N,m) with m in {3,6,9}.  Values are written with repr() of a
    python float, which is the shortest round-trip representation, so the ascii
    round trip is bit-exact (the frozen grader's own _write_scalar_field uses the
    same convention).
    """
    a = np.asarray(values, dtype=float)
    if a.ndim == 1:
        a = a.reshape(-1, 1)
    if a.ndim != 2 or a.shape[1] not in _NCOMP_CLASS:
        refuse(f"write_field_ascii: shape {a.shape} is not (N,) or (N,m) with "
               f"m in {sorted(_NCOMP_CLASS)}")
    if not np.all(np.isfinite(a)):
        refuse("write_field_ascii: refusing to write non-finite values")
    tname, cname = _NCOMP_CLASS[a.shape[1]]
    n, m = a.shape
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
                 f"    class       {cname};\n    location    \"{iteration}\";\n"
                 f"    object      {field};\n"
                 f"    note        \"{synthetic_note}\";\n}}\n\n"
                 "dimensions      [0 0 0 0 0 0 0];\n\n"
                 f"internalField   nonuniform List<{tname}>\n{n}\n(\n")
        if m == 1:
            for row in a:
                fh.write(f"{float(row[0])!r}\n")
        else:
            for row in a:
                fh.write("(" + " ".join(repr(float(v)) for v in row) + ")\n")
        fh.write(")\n;\n")
    return path


# ============================================================================
#  THE WRITER
# ============================================================================
def _check_sequence_registered(iters, ends_at, kmin):
    """The registered proviso, PREREGISTRATION.md item 1 line 111:
    'consecutive outer iterates ending at the write iteration'.

    Enforced here for BOTH registered mechanisms; the writer does not decide
    WHICH iteration `ends_at` is - the caller (the mechanism front-end) names it.
    """
    need = kmin + 2
    if len(iters) < need:
        refuse(f"{len(iters)} snapshots; the frozen criterion needs >= "
               f"DFP_KMIN+2 = {need} to measure a {kmin}-ratio contraction "
               f"(grade_r5d.py:distance_to_fixed_point)")
    for a, b in zip(iters, iters[1:]):
        if b != a + 1:
            refuse(f"iterations {iters} are NOT consecutive ({a} -> {b}); the "
                   f"registered proviso is 'consecutive outer iterates' "
                   f"(PREREGISTRATION.md item 1)")
    if iters[-1] != ends_at:
        refuse(f"sequence ends at iteration {iters[-1]}, not at the declared "
               f"end iteration {ends_at}; the registered proviso is 'ending at "
               f"the write iteration' (PREREGISTRATION.md item 1)")


def write_snapshots(case_dir, field, pairs, ends_at, grader,
                    replace_stale=False, write_iter=None, arrays=None):
    """Normalise consecutive outer iterates into <case_dir>/dfpSnaps/<field>_<iter>.

    pairs      : [(iter:int, source_path:str|None), ...] ascending.
    arrays     : optional {iter: ndarray} for the SYNTHETIC path (source_path None).
    ends_at    : the iteration the sequence must end at (caller-declared).
    write_iter : the case's actual write iteration, if known; recorded in the
                 manifest as `ends_at_write_iter` so the supervisor can see, per
                 case, whether the tail ends AT the graded field (mechanism A) or
                 PAST it (mechanism B).  Never guessed here.
    Returns the manifest dict.  Refuses (exit 2) rather than degrading.
    """
    kmin = int(grader.DFP_KMIN)
    iters = [int(i) for i, _ in pairs]
    if iters != sorted(iters):
        refuse(f"iterations {iters} are not ascending")
    _check_sequence_registered(iters, int(ends_at), kmin)

    snapdir = os.path.join(case_dir, SNAPDIR)
    os.makedirs(snapdir, exist_ok=True)

    # --- stale-sequence guard: the frozen reader globs EVERY <field>_<digits>
    #     in this directory, so a leftover from an earlier attempt would silently
    #     become part of the graded sequence.
    keep = {f"{field}_{i}" for i in iters}
    stale = sorted(n for n in os.listdir(snapdir)
                   if re.match(rf"{re.escape(field)}_(\d+)$", n) and n not in keep)
    removed = []
    if stale:
        if not replace_stale:
            refuse(f"{snapdir} already holds snapshots the frozen reader would "
                   f"include in the sequence but this call does not write: "
                   f"{stale}.  Refusing to silently mix two sequences; pass "
                   f"--replace to remove exactly these files.")
        for n in stale:
            os.remove(os.path.join(snapdir, n))
            removed.append(n)

    # --- write ---------------------------------------------------------------
    rows, shape0 = [], None
    for it, src in pairs:
        dst = os.path.join(snapdir, f"{field}_{it}")
        if src is not None:
            pre = read_or_refuse(src, f"source iterate {it}")   # reader is authority
            shutil.copyfile(src, dst)                            # byte-for-byte
            mode = "byte-copy"
        else:
            if arrays is None or it not in arrays:
                refuse(f"iterate {it}: neither a source path nor an array given")
            pre = np.asarray(arrays[it], dtype=float)
            write_field_ascii(dst, pre, field, it,
                              "SYNTHETIC/CONTROL - written by write_dfp_snaps.py "
                              "array path, NOT solver output")
            mode = "array"
        if shape0 is None:
            shape0 = pre.shape
        elif pre.shape != shape0:
            refuse(f"iterate {it}: field shape {pre.shape} != {shape0} of the "
                   f"first iterate; the sequence is not one field")
        rows.append({"iter": it, "mode": mode, "source": src,
                     "shape": list(pre.shape),
                     "l2_source": float(np.linalg.norm(np.asarray(pre).ravel())),
                     "sha256": sha256_file(dst)})

    # --- VERIFY THROUGH THE FROZEN READER ------------------------------------
    # A writer that was never read back by the instrument that will grade it is
    # not a writer.  This is the writer's own planted control: it must be able to
    # see its own bad write.
    snaps = grader.load_snapshots(case_dir, field)
    if snaps is None:
        refuse(f"post-write verify: the FROZEN load_snapshots returned None for "
               f"field {field} in {case_dir} - the reader cannot see what was "
               f"just written")
    if len(snaps) != len(iters):
        refuse(f"post-write verify: the FROZEN reader returned {len(snaps)} "
               f"snapshots, {len(iters)} were written (stale or shadowed files "
               f"in {snapdir})")
    for k, (r, s) in enumerate(zip(rows, snaps)):
        got = float(np.linalg.norm(np.asarray(s).ravel()))
        want = r["l2_source"]
        den = max(abs(want), 1e-300)
        if abs(got - want) / den > 0.0:
            refuse(f"post-write verify: iterate {r['iter']} read back with L2 "
                   f"{got!r} != source L2 {want!r} (rel {(got - want) / den:.3e}); "
                   f"the round trip is not exact")
        r["l2_readback"] = got
        r["readback_size"] = int(np.asarray(s).size)

    man = {
        "written_by": "write_dfp_snaps.py (UNFROZEN run-side producer; NOT part "
                      "of R5D's frozen grading path)",
        "writer_sha256": sha256_file(os.path.abspath(__file__)),
        "written_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "case_dir": os.path.abspath(case_dir),
        "field": field,
        "iters": iters,
        "n_snaps": len(iters),
        "dfp_kmin": kmin,
        "min_required": kmin + 2,
        "ends_at": int(ends_at),
        "case_write_iter": (None if write_iter is None else int(write_iter)),
        "ends_at_write_iter": (None if write_iter is None
                               else bool(int(ends_at) == int(write_iter))),
        "consecutive": True,
        "stale_removed": removed,
        "frozen_grader": GRADER_PATH,
        "frozen_grader_sha256": GRADER_SHA_PIN,
        "frozen_constants": {"DFP_KMIN": grader.DFP_KMIN,
                             "DFP_CV_FLOOR": grader.DFP_CV_FLOOR,
                             "DFP_STAR_TARGET": grader.DFP_STAR_TARGET,
                             "DFP_STAR_OMEGA": grader.DFP_STAR_OMEGA,
                             "DFP_RATIO_STAB": grader.DFP_RATIO_STAB},
        "frozen_reader_verified": True,
        "snapshots": rows,
        "note": "The frozen grade_r5d.py:load_snapshots does NOT read this "
                "manifest.  It is supervisor-checkable provenance, not a gate.",
    }
    mpath = os.path.join(snapdir, MANIFEST)
    old = {}
    if os.path.exists(mpath):
        try:
            old = json.load(open(mpath))
        except Exception:                        # noqa: BLE001
            old = {}
    if not isinstance(old, dict) or "fields" not in old:
        old = {"fields": {}}
    old["fields"][field] = man
    with open(mpath, "w") as fh:
        json.dump(old, fh, indent=2, sort_keys=True)
    return man


# ------------------------------------------------------- source resolution
def resolve_from_time_dirs(case_dir, field, ends_at, n):
    """Both registered mechanisms deposit per-iteration OpenFOAM TIME DIRECTORIES;
    this turns the last `n` of them, ending at `ends_at`, into (iter, path) pairs.

    Chooses no mechanism: it only reads what is already on disk.
    """
    have = []
    for name in os.listdir(case_dir):
        m = _ITER_RE.match(name)
        if m and os.path.isdir(os.path.join(case_dir, name)):
            have.append(int(name))
    have = sorted(i for i in have if i <= int(ends_at))
    if int(ends_at) not in have:
        refuse(f"{case_dir}: no time directory {ends_at} (found "
               f"{have[-8:] if have else 'none'}); the sequence cannot end at "
               f"the declared end iteration")
    want = list(range(int(ends_at) - n + 1, int(ends_at) + 1))
    missing = [i for i in want if i not in have]
    if missing:
        refuse(f"{case_dir}: time directories {missing} absent, so the last {n} "
               f"outer iterates ending at {ends_at} are not all on disk.  The "
               f"run must save every iterate in the window (PREREGISTRATION.md "
               f"item 1) - no gap may be interpolated.")
    pairs = []
    for i in want:
        p = os.path.join(case_dir, str(i), field)
        if not os.path.isfile(p):
            refuse(f"{p} absent: iterate {i} has no {field} field")
        pairs.append((i, p))
    return pairs


# ============================================================================
#  --selftest   (green under python3 AND python3 -O)
# ============================================================================
def _predict_d_rel(shape_vec, eps, q, n_snaps):
    """Analytic d_rel for f_k = fstar + eps*shape*q^k, k = 0..N (N = n_snaps-1).

    s_k = eps*||shape||*(1-q)*q^(k-1);  r_k = q exactly (so rho = q, and
    max/min = 1 <= DFP_RATIO_STAB, i.e. CONVERGING);
    D = s_N/(1-q) = eps*||shape||*q^(N-1);  d_rel = D/||f_N||.
    (The true distance ||f_N - fstar|| is eps*||shape||*q^N, so the frozen
    estimator overshoots by exactly 1/q - it is conservative.)
    """
    n = int(n_snaps) - 1
    return float(eps * np.linalg.norm(np.asarray(shape_vec).ravel()) * q ** (n - 1))


def selftest():
    t0 = time.time()
    print("=" * 74)
    print("write_dfp_snaps.py --selftest   (UNFROZEN run-side producer)")
    print("=" * 74)
    grader, gsha = load_frozen_grader()
    print(f"frozen grade_r5d.py sha256 {gsha}  == PREREGISTRATION.md sec.7 pin")
    print(f"writer sha256              {sha256_file(os.path.abspath(__file__))}")
    kmin = int(grader.DFP_KMIN)
    need = kmin + 2
    dstar = float(grader.DFP_STAR_TARGET)
    print(f"frozen constants: DFP_KMIN={kmin} (needs {need} snapshots), "
          f"DFP_STAR_TARGET={dstar:g}, DFP_CV_FLOOR={grader.DFP_CV_FLOOR:g}, "
          f"DFP_RATIO_STAB={grader.DFP_RATIO_STAB:g}")

    root = SELFTEST_ROOT
    if os.path.abspath(root).startswith(os.path.abspath(R5D_RUN_ROOT)):
        refuse("selftest root is inside the R5D run root; refusing to "
               "contaminate a graded case directory")
    if os.path.isdir(root):
        shutil.rmtree(root)
    os.makedirs(root)
    ok_all = True
    fired = 0

    def check(name, cond, detail=""):
        nonlocal ok_all
        ok_all = ok_all and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}"
              + (f"  -- {detail}" if detail else ""))

    def must_refuse(name, fn):
        """A refusal control PASSES only when the refusal actually FIRES."""
        nonlocal fired
        try:
            fn()
        except SystemExit as e:
            if e.code == 2:
                fired += 1
                check(name + "  [REFUSAL FIRED]", True)
                return
            check(name, False, f"exited {e.code}, expected 2")
            return
        check(name, False, "NO refusal fired - the guard is blind")

    # ---- control 0: no assert carries a guard (L-332 / D476 sec.31.3) --------
    print("\n[0] no `assert` carries any guard (stripped under python3 -O)")
    na = no_assert_in_this_file()
    check("ast.Assert count in this file == 0", na == 0, f"count {na}")

    # ---- control 1: PLANTED geometric contraction, d_rel PREDICTED ----------
    print(f"\n[1] planted contraction: the FROZEN reader must return a "
          f"PREDICTED non-zero d_rel")
    rng = np.random.default_rng(20260910)
    shape = rng.random(500)
    fstar = 5.0 + shape                       # spatially varied: cv >> CV_FLOOR
    # eps is chosen so the PERTURBATION stays far above the float64 ulp of the
    # base field: the analytic-prediction control below tests the arithmetic
    # model, whose floating-point floor is ~ulp(||f||)/(d_rel*sqrt(ncells)), NOT
    # the writer.  The writer's own claim - that the ascii round trip loses
    # nothing - is tested separately, at tolerance EXACTLY zero.
    for tag, eps, q, expect_conv in (("converged", 4e-6, 0.5, True),
                                     ("damped-L243", 1e-3, 0.999, False)):
        cdir = os.path.join(root, f"case_{tag}")
        os.makedirs(cdir)
        wi = 120
        iters = list(range(wi - need + 1, wi + 1))
        arrs = {it: fstar + eps * shape * (q ** k) for k, it in enumerate(iters)}
        write_snapshots(cdir, "kDeficit", [(i, None) for i in iters], wi, grader,
                        write_iter=wi, arrays=arrs)
        snaps = grader.load_snapshots(cdir, "kDeficit")
        check(f"[{tag}] FROZEN load_snapshots consumed the written sequence",
              snaps is not None and len(snaps) == need,
              f"{0 if snaps is None else len(snaps)} snapshots, "
              f"iters {iters[0]}..{iters[-1]}")
        d = grader.distance_to_fixed_point(snaps, dstar)
        # (a) THE WRITER'S OWN CLAIM: what the frozen reader gets back off disk
        #     is what was handed to the writer, to the last bit.  Tolerance 0.
        d_mem = grader.distance_to_fixed_point([np.asarray(arrs[i]).ravel()
                                                for i in iters], dstar)
        check(f"[{tag}] ascii round trip is EXACT (disk d_rel == in-memory d_rel)",
              d["d_rel"] == d_mem["d_rel"] and d["rho"] == d_mem["rho"],
              f"disk {d['d_rel']!r} vs memory {d_mem['d_rel']!r}, "
              f"difference exactly {d['d_rel'] - d_mem['d_rel']!r}")
        # (b) the arithmetic model, at an fp-justified tolerance
        pred_D = _predict_d_rel(shape, eps, q, need)
        pred = pred_D / float(np.linalg.norm(np.asarray(arrs[iters[-1]]).ravel()))
        got = d["d_rel"]
        rel = abs(got - pred) / pred
        check(f"[{tag}] FROZEN reader returned a DISTANCE (not None, not zero)",
              got is not None and got > 0.0, f"d_rel = {got:.6e}")
        check(f"[{tag}] d_rel matches the analytic prediction",
              rel <= 1e-6, f"predicted {pred:.9e}, measured {got:.9e}, "
                           f"rel err {rel:.2e} <= 1e-6 (fp floor of the "
                           f"construction, not of the writer)")
        check(f"[{tag}] rho recovers q, sequence CONVERGING",
              d["seq"] == "CONVERGING" and abs(d["rho"] - q) / q <= 1e-6,
              f"seq={d['seq']} rho={d['rho']!r} (q={q})")
        check(f"[{tag}] converged verdict against the {dstar:g} bar is {expect_conv}",
              bool(d["converged"]) is expect_conv,
              f"converged={d['converged']} d_rel={got:.3e} vs bar {dstar:g}")
    # a blind reader (returns 0) would NOT reproduce a predicted non-zero
    check("a reader returning 0 would fail the predicted-value control",
          not (abs(0.0 - pred) / pred <= 1e-6))

    # ---- control 2: refusals the FROZEN reader must fire --------------------
    print("\n[2] the FROZEN reader's own refusals, through files THIS writer wrote")
    cdir = os.path.join(root, "case_flat")
    os.makedirs(cdir)
    iters = list(range(116, 116 + need))
    flat = {it: np.full(500, 7.0) for it in iters}
    # the writer's own cv guard is deliberately NOT applied here: we want the
    # FROZEN reader to be the one that refuses, on real files on disk.
    write_snapshots(cdir, "kDeficit", [(i, None) for i in iters], iters[-1],
                    grader, write_iter=iters[-1], arrays=flat)
    d = grader.distance_to_fixed_point(grader.load_snapshots(cdir, "kDeficit"), dstar)
    check("flat/clipped sequence -> FROZEN reader REFUSE fired (L-235)",
          bool(d["refuse"]) and not d["converged"], d["reason"])
    fired += 1 if d["refuse"] else 0

    cdir = os.path.join(root, "case_cliff")
    os.makedirs(cdir)
    base = [fstar + shape * (0.5 ** k) for k in range(3)]
    seq = base + [base[-1], base[-1]]          # steps collapse to EXACTLY 0
    iters = list(range(200, 200 + len(seq)))
    write_snapshots(cdir, "kDeficit", [(i, None) for i in iters], iters[-1],
                    grader, write_iter=iters[-1],
                    arrays=dict(zip(iters, seq)))
    d = grader.distance_to_fixed_point(grader.load_snapshots(cdir, "kDeficit"), dstar)
    check("cliff (step collapses to exactly 0) -> FROZEN reader REFUSE fired",
          bool(d["refuse"]) and not d["converged"], d["reason"])
    fired += 1 if d["refuse"] else 0

    # ---- control 3: the WRITER's own refusals must fire ---------------------
    print("\n[3] the writer's own guards - each must FIRE, not merely exist")
    cdir = os.path.join(root, "case_guards")
    os.makedirs(cdir)
    good_iters = list(range(96, 96 + need))
    good_arrs = {it: fstar + 1e-9 * shape * (0.5 ** k)
                 for k, it in enumerate(good_iters)}
    must_refuse("too few snapshots (< DFP_KMIN+2) -> refuse",
                lambda: write_snapshots(cdir, "kDeficit",
                                        [(i, None) for i in good_iters[:need - 1]],
                                        good_iters[need - 2], grader,
                                        arrays=good_arrs))
    gap = good_iters[:2] + [good_iters[2] + 7] + good_iters[3:]
    must_refuse("non-consecutive iterates -> refuse",
                lambda: write_snapshots(cdir, "kDeficit", [(i, None) for i in gap],
                                        gap[-1], grader,
                                        arrays={i: fstar + shape for i in gap}))
    must_refuse("sequence does not end at the declared end iteration -> refuse",
                lambda: write_snapshots(cdir, "kDeficit",
                                        [(i, None) for i in good_iters],
                                        good_iters[-1] + 1, grader,
                                        arrays=good_arrs))
    # a `uniform` placeholder is UNREADABLE by the frozen reader
    upath = os.path.join(root, "uniform_kDeficit")
    with open(upath, "w") as fh:
        fh.write("FoamFile\n{\n version 2.0;\n format ascii;\n"
                 " class volScalarField;\n object kDeficit;\n}\n"
                 "internalField   uniform 0;\n")
    must_refuse("`uniform` placeholder source (reader cannot parse) -> refuse",
                lambda: write_snapshots(cdir, "kDeficit",
                                        [(i, upath) for i in good_iters],
                                        good_iters[-1], grader))
    # stale leftovers the frozen reader WOULD have globbed into the sequence
    cdir2 = os.path.join(root, "case_stale")
    os.makedirs(cdir2)
    write_snapshots(cdir2, "kDeficit", [(i, None) for i in good_iters],
                    good_iters[-1], grader, write_iter=good_iters[-1],
                    arrays=good_arrs)
    must_refuse("stale <field>_<iter> from an earlier attempt -> refuse",
                lambda: write_snapshots(cdir2, "kDeficit",
                                        [(i, None) for i in range(300, 300 + need)],
                                        300 + need - 1, grader,
                                        arrays={i: fstar + shape
                                                for i in range(300, 300 + need)}))
    n_before = len(grader.load_snapshots(cdir2, "kDeficit"))
    write_snapshots(cdir2, "kDeficit",
                    [(i, None) for i in range(300, 300 + need)], 300 + need - 1,
                    grader, replace_stale=True, write_iter=300 + need - 1,
                    arrays={i: fstar + 1e-9 * shape * (0.5 ** k)
                            for k, i in enumerate(range(300, 300 + need))})
    n_after = len(grader.load_snapshots(cdir2, "kDeficit"))
    check("--replace removes exactly the stale files (reader sees one sequence)",
          n_before == need and n_after == need,
          f"before {n_before}, after {n_after}, both == {need}")

    # ---- control 4: the post-write verify can SEE a bad write ---------------
    print("\n[4] blind-writer control: the post-write verify must catch corruption")
    cdir3 = os.path.join(root, "case_corrupt")
    os.makedirs(cdir3)
    write_snapshots(cdir3, "kDeficit", [(i, None) for i in good_iters],
                    good_iters[-1], grader, write_iter=good_iters[-1],
                    arrays=good_arrs)
    victim = os.path.join(cdir3, SNAPDIR, f"kDeficit_{good_iters[1]}")
    shutil.copyfile(upath, victim)               # corrupt one snapshot in place
    corrupt_caught = False
    try:
        grader.load_snapshots(cdir3, "kDeficit")
    except Exception:                            # noqa: BLE001
        corrupt_caught = True
    check("a corrupted snapshot is NOT silently readable by the frozen reader",
          corrupt_caught, "of_read.read_field raises on the `uniform` placeholder")
    must_refuse("re-writing over the corrupted case re-reads and refuses the "
                "unreadable source -> refuse",
                lambda: write_snapshots(cdir3, "kDeficit",
                                        [(i, victim) for i in good_iters],
                                        good_iters[-1], grader,
                                        replace_stale=True))

    # ---- control 5: PENDING is honest - no dfpSnaps, no fabrication ---------
    print("\n[5] absent dfpSnaps -> the frozen reader returns None (PENDING)")
    empty = os.path.join(root, "case_no_snaps")
    os.makedirs(empty)
    check("no dfpSnaps -> load_snapshots None, no distance fabricated",
          grader.load_snapshots(empty, "kDeficit") is None)
    d = grader.distance_to_fixed_point([], dstar)
    check("empty sequence -> not converged, no distance",
          (not d["converged"]) and d["d_rel"] is None, d["reason"])

    # ---- control 6: MANIFEST.json does not enter the graded sequence --------
    print("\n[6] the manifest is invisible to the frozen reader's regex")
    mpath = os.path.join(os.path.join(root, "case_converged"), SNAPDIR, MANIFEST)
    check("MANIFEST.json written beside the snapshots",
          os.path.exists(mpath), mpath)
    check("frozen reader still returns exactly the snapshot count",
          len(grader.load_snapshots(os.path.join(root, "case_converged"),
                                    "kDeficit")) == need)

    # ---- control 7: REAL OpenFOAM output, scalar AND symmTensor -------------
    print("\n[7] real OpenFOAM fields (byte-copy path + symmTensor dialect)")
    donor_case = "/home/ubuntu/closure-data/r5c/frozen/AR_10_Ret_180"
    donor_t = "1654"
    if not os.path.isdir(os.path.join(donor_case, donor_t)):
        check("real donor case present (R5C run output, READ ONLY)", False,
              f"{donor_case}/{donor_t} absent - real-data control SKIPPED")
    else:
        cdir4 = os.path.join(root, "case_real")
        os.makedirs(cdir4)
        for fld, eps, q, expect_conv in (("kDeficit", 1e-3, 0.5, False),
                                         ("bijDelta", 1e-7, 0.5, True)):
            src = os.path.join(donor_case, donor_t, fld)
            ref = np.asarray(of_read.read_field(src), dtype=float)
            # 7a byte-copy path on the solver's own file
            cbc = os.path.join(root, f"case_bytecopy_{fld}")
            os.makedirs(cbc, exist_ok=True)
            bits = list(range(50, 50 + need))
            write_snapshots(cbc, fld, [(i, src) for i in bits], bits[-1], grader,
                            write_iter=bits[-1])
            rb = grader.load_snapshots(cbc, fld)
            check(f"[{fld}] byte-copy of real OpenFOAM output read back bit-exact "
                  f"by the FROZEN reader",
                  rb is not None and len(rb) == need
                  and float(np.linalg.norm(rb[-1]))
                  == float(np.linalg.norm(ref.ravel())),
                  f"shape {ref.shape}, L2 {np.linalg.norm(ref.ravel()):.9e}")
            # 7b a predicted contraction built on the real field
            iters = list(range(1654 - need + 1, 1655))
            arrs = {it: ref * (1.0 + eps * (q ** k))
                    for k, it in enumerate(iters)}
            write_snapshots(cdir4, fld, [(i, None) for i in iters], 1654, grader,
                            write_iter=1654, arrays=arrs)
            snaps = grader.load_snapshots(cdir4, fld)
            d = grader.distance_to_fixed_point(snaps, dstar)
            n = need - 1
            pred = (eps * float(np.linalg.norm(ref.ravel())) * q ** (n - 1)
                    / float(np.linalg.norm(np.asarray(arrs[1654]).ravel())))
            rel = abs(d["d_rel"] - pred) / pred
            check(f"[{fld}] real-field contraction: FROZEN reader returns the "
                  f"PREDICTED d_rel",
                  rel <= 1e-6 and d["seq"] == "CONVERGING",
                  f"predicted {pred:.6e}, measured {d['d_rel']:.6e}, "
                  f"rel err {rel:.2e}, seq={d['seq']}")
            check(f"[{fld}] converged against the {dstar:g} bar is {expect_conv}",
                  bool(d["converged"]) is expect_conv,
                  f"converged={d['converged']}")

    dt = time.time() - t0
    print("\n" + "=" * 74)
    print(f"refusal controls that FIRED: {fired}  (a selftest that only ever "
          f"passes is the weak test)")
    print(f"SELFTEST {'GREEN' if ok_all else 'RED'}   wall {dt:.2f} s, 1 rank "
          f"= {dt / 60.0:.4f} core-min")
    print("This writer asserts NO verdict and is NOT frozen.")
    print("=" * 74)
    return 0 if ok_all else 1


# ============================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Write the R5D dfpSnaps per-iteration snapshot sequence the "
                    "FROZEN grade_r5d.py:load_snapshots reads.  Run-side "
                    "producer; chooses neither registered capture mechanism.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--case", help="case directory (dfpSnaps/ is created inside)")
    ap.add_argument("--field", action="append", default=None,
                    help="field name; repeatable (omega kDeficit bijDelta)")
    ap.add_argument("--ends-at", type=int,
                    help="the outer iteration the sequence must END at "
                         "(registered proviso, PREREGISTRATION.md item 1)")
    ap.add_argument("--write-iter", type=int, default=None,
                    help="the case's actual write iteration, if known; recorded "
                         "in the manifest as ends_at_write_iter")
    ap.add_argument("--n", type=int, default=None,
                    help="how many iterates (default DFP_KMIN+2 from the frozen "
                         "grader)")
    ap.add_argument("--from", dest="src", default=None,
                    help="iter=path[,iter=path...] explicit sources; default is "
                         "the case's own per-iteration time directories")
    ap.add_argument("--replace", action="store_true",
                    help="remove exactly the stale <field>_<iter> files first")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.case or not args.field or args.ends_at is None:
        ap.error("--case, --field and --ends-at are required (or --selftest)")
    grader, gsha = load_frozen_grader()
    n = args.n if args.n is not None else int(grader.DFP_KMIN) + 2
    if not os.path.isdir(args.case):
        refuse(f"case directory absent: {args.case}")
    print(f"frozen grade_r5d.py sha256 {gsha} == PREREGISTRATION.md sec.7 pin")
    for field in args.field:
        if args.src:
            pairs = []
            for tok in args.src.split(","):
                if "=" not in tok:
                    refuse(f"--from token {tok!r} is not iter=path")
                it, p = tok.split("=", 1)
                pairs.append((int(it), p))
            pairs.sort(key=lambda t: t[0])
        else:
            pairs = resolve_from_time_dirs(args.case, field, args.ends_at, n)
        man = write_snapshots(args.case, field, pairs, args.ends_at, grader,
                              replace_stale=args.replace,
                              write_iter=args.write_iter)
        print(f"  {field}: wrote {man['n_snaps']} snapshots "
              f"{man['iters'][0]}..{man['iters'][-1]} -> "
              f"{os.path.join(args.case, SNAPDIR)}  "
              f"[FROZEN reader verified round-trip]"
              + ("" if man["ends_at_write_iter"] is None else
                 f"  ends_at_write_iter={man['ends_at_write_iter']}"))
    print("dfpSnaps written.  No verdict is asserted by this writer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
