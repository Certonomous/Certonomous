#!/usr/bin/env python3
r"""Curriculum D19R -- THE REPAIRED AGE DATUM, AND THE CONTROLS THAT PROVE IT CAN
STILL REFUSE.

WHAT BROKE IN D19, MEASURED AND NOT INFERRED
============================================
`CLAUDE.md` rule 4 dates a run by "the case's own `0/T`", on the stated premise
that `0/T` "is touched last at launch and so dates the run allowed to produce the
answer".  D19's launcher generalised that to: touch every file in the arm's `0/`,
record `<max mtime> <file count> <dir>`, and require the grader to re-derive the
same pair.  It refused arm `S1` with

    REFUSE G1  age_datum_moved  S1/0  recorded 1788213189  rederived 1788213232

**The premise is false for DAFoam, and the refusal was correct behaviour enforcing
a false premise.**  Measured this invocation, from the D19 run root:

  1. `S1/0/U.gz` mtime 1788213232 == the rederived datum, 43 s into a 51 s run.
  2. `S1/0/U.gz` carries `internalField nonuniform List<vector> 4032` -- a
     CONVERGED field.  `S1/0.orig/U` carries `internalField uniform (100 0 0)`.
     So the solver rewrote the file; it did not merely touch it.
  3. That write's `inout` patch reads
     `inletValue uniform (99.75762098674072 6.958236491079174 0)`;
     `atan(6.958236/99.757621) = 3.99 deg`, which is exactly the item's last
     evaluation, `patchV[1] - 0.01`, off a 4.0 deg baseline.  **The `patchV`
     design variable is applied by REWRITING `0/U`'s inlet boundary condition**,
     and OpenFOAM writes the whole object -- internalField included -- under
     `writeCompression on`.
  4. **IT IS NOT A SERIAL-ARM DEFECT.**  `S2/processor0/0/U.gz` was rewritten the
     same way, mid-run, mtime 1788213122, `nonuniform List<vector> 2016`.  The
     serial arm is only the arm where the rewrite lands in the directory the
     guard watches.  A repair scoped to "the serial case" would leave the
     parallel arms guarded by luck rather than by a true premise.
  5. **A SECOND DEFECT NOBODY HAS REPORTED: THE COUNT CHECK PASSED BY
     COINCIDENCE.**  `S1/0` held 9 files before and 9 after -- but SIX of the nine
     filenames changed (`T`->`T.gz`, `U`->`U.gz`, `p`->`p.gz`, `nut`->`nut.gz`,
     `nuTilda`->`nuTilda.gz`, `alphat`->`alphat.gz`).  A count is not an identity.
     Had the mtime clause not fired, the count clause would have waved through a
     directory whose every graded file had been replaced.

THE REPAIR -- THREE LEGS, AND THE AGE ASSERTION IS NOT WEAKENED
===============================================================
L1  THE DATUM LEAVES THE SOLVER'S WRITE SET, STRUCTURALLY.  The launcher stamps a
    sentinel OUTSIDE every bind-mount source.  D19's launcher runs
    `docker run ... -v "$BASE":/mnt`, so `$BASE` and everything under it is
    writable by the solve; `$BASE`'s PARENT is not mounted.  The sentinel lives at
    `<parent of run root>/.d19r_datums/<ARM>.sentinel`.  This is ASSERTED, not
    hoped: `assert_sentinel_outside_mounts()` refuses if the sentinel path is at
    or under any declared mount source.  "The solver does not write here" stops
    being a belief about DAFoam and becomes a property of the mount namespace.

L2  THE AGE ASSERTION IS RULE 4's, UNCHANGED.  Every graded artefact's mtime must
    be STRICTLY GREATER than the sentinel epoch.  Nothing is deleted, bypassed,
    softened to `>=`, or given a tolerance.  Only the datum's PROVENANCE changed.

L3  CONTENT IDENTITY REPLACES THE COUNT.  At stage time the launcher records an
    md5 manifest of the arm's INPUT set -- the files that must not change.  The
    grader asserts every entry byte-identical.  `0/` and `processor*/` are
    EXCLUDED BY NAME, with the reason recorded in the manifest itself, because
    they are solver write targets: a guard must not assert a premise the solver
    falsifies.  This is strictly stronger than the count it replaces (it catches
    a wholly-replaced directory of unchanged cardinality) and strictly narrower
    in what it claims about `0/`.

WHAT THIS GUARD STILL REFUSES -- and `--selftest` DRIVES EVERY ONE OF THESE RED
==============================================================================
    RED-1  artefact OLDER than the sentinel        -> REFUSE  (the stale answer)
    RED-2  artefact mtime EQUAL to the sentinel    -> REFUSE  (strictly greater)
    RED-3  a manifest input's CONTENT changed      -> REFUSE  (L3 has teeth)
    RED-4  sentinel inside a declared mount source -> REFUSE  (L1 has teeth)
    RED-5  manifest entry missing from disk        -> REFUSE
    GREEN-1 THE D19 REGRESSION: artefact newer, `0/U` legitimately rewritten
            AFTER the sentinel, `0/T` replaced by `0/T.gz`  -> ACCEPT
    GREEN-2 clean case                                       -> ACCEPT

A guard that cannot fail is not a guard.  This lab certified one such guard
earlier today and had to retract it, so the red legs are run at freeze and their
output is quoted in the pre-registration.

THE RELATIVE PLANTED CONTROL (`CLAUDE.md` rule 3), SIZED TO THE BAND
====================================================================
`SO-2M` was lost to a bare ABSOLUTE plant of 1.234e-03 that turned out to be
2.48 % of its own reference and could not cross its own 5 % band.  A plant that
cannot cross the band it is asked to cross proves nothing.  So the plant is sized
RELATIVE, and its size is registered at freeze:

    plant_i = K * (band/100) * |d_ref_i|          K = 5.0, registered

with `band` the gate's own band in percent and `d_ref_i` the reference value the
plant perturbs.  K = 5.0 moves the reading by `5 * band` percentage points -- a
5x margin over the band, so a reader that cannot see it is broken rather than
merely insensitive.

AND THE SUFFICIENCY LEG IS DRIVEN RED, which is the half that has teeth: the same
control re-run at `K_shrunk = 0.5` moves the reading by HALF the band and MUST
report NOT-CROSSED.  A control that reports "crossed" at every plant size is not
measuring crossing; it is measuring nothing.  Both legs run at freeze.

Usage:  d19r_age_guard.py --selftest
        (as a library: stamp_sentinel / check_arm / plant_relative)
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time

ITEM = "D19R"
SENTINEL_DIRNAME = ".d19r_datums"

# --- registered plant constants (PREREGISTRATION.md G19R-1c) ------------------
PLANT_K = 5.0            # sufficiency: must cross the band with a 5x margin
PLANT_K_SHRUNK = 0.5     # sufficiency RED leg: must NOT cross (half the band)

# Directories that are SOLVER WRITE TARGETS and are therefore excluded from the
# input manifest BY NAME.  Measured, not assumed -- see the module docstring.
SOLVER_WRITE_TARGETS = ("0", "processor")


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ============================================================================
# L1 -- the sentinel, and the assertion that it is outside every mount source
# ============================================================================
def sentinel_path(run_root, arm):
    """Outside the run root, hence outside `-v <run root>:/mnt`."""
    return os.path.join(os.path.dirname(os.path.abspath(run_root)),
                        SENTINEL_DIRNAME, os.path.basename(os.path.abspath(run_root)),
                        "%s.sentinel" % arm)


def _under(path, root):
    p = os.path.realpath(path)
    r = os.path.realpath(root)
    return p == r or p.startswith(r.rstrip(os.sep) + os.sep)


def assert_sentinel_outside_mounts(spath, mount_sources):
    """L1 with teeth.  `mount_sources` is what the launcher actually passes to
    `docker run -v <src>:<dst>`; the caller reads it from its own command line,
    never from recollection."""
    for src in mount_sources:
        if _under(spath, src):
            refuse("AGE_DATUM_INSIDE_MOUNT",
                   {"sentinel": spath, "mount_source": src,
                    "note": "the datum would be writable by the solve -- this is "
                            "exactly the D19 defect and it is refused at launch"})
    return True


def stamp_sentinel(run_root, arm, mount_sources):
    """Called by the launcher AFTER staging and BEFORE the container starts."""
    spath = sentinel_path(run_root, arm)
    assert_sentinel_outside_mounts(spath, mount_sources)
    os.makedirs(os.path.dirname(spath), exist_ok=True)
    with open(spath, "w") as fh:
        fh.write("%s %s\n" % (ITEM, arm))
        fh.flush()
        os.fsync(fh.fileno())
    return spath, os.stat(spath).st_mtime          # full precision -- see check_arm


# ============================================================================
# L3 -- the input manifest, by CONTENT, with the write targets excluded by name
# ============================================================================
def is_write_target(name):
    head = name.split(os.sep)[0]
    return head in SOLVER_WRITE_TARGETS or head.startswith("processor")


def build_manifest(arm_dir, input_subdirs):
    entries, excluded = [], []

    # ---- THE EXCLUSION IS ENFORCING, NOT DESCRIPTIVE -----------------------
    # Found by the dafoam-supervisor's adversarial probe at check 1 and
    # reproduced by this lane: the `excluded` list below is built by LISTING the
    # arm, while `entries` are built from the CALLER's `input_subdirs`, and
    # nothing made the two agree.  `build_manifest(arm, ["0", "system"])`
    # produced a manifest whose `excluded_write_targets` field said `["0"]`
    # while its own entries pinned `0/T` and `0/U` -- **a record asserting
    # something the code did not guarantee**, which is the defect class that has
    # burned this lab repeatedly.  It was fail-closed (it would refuse every run,
    # never pass a bad one), so it was never a correctness hole; it was a false
    # assertion, and a false assertion in an evidence artefact is the thing this
    # guard exists to prevent.
    #
    # It REFUSES rather than silently filtering `input_subdirs`, so a caller's
    # mistake is SURFACED rather than absorbed.  Driven red by RED-7.
    for sub in input_subdirs:
        if is_write_target(sub):
            refuse("MANIFEST_INPUT_IS_WRITE_TARGET",
                   {"input_subdir": sub,
                    "write_targets": list(SOLVER_WRITE_TARGETS) + ["processor*"],
                    "note": "a manifest may not pin a path the solver writes -- that "
                            "is the D19 age-datum defect in a second location.  The "
                            "caller is refused, not silently corrected."})

    for name in sorted(os.listdir(arm_dir)):
        full = os.path.join(arm_dir, name)
        if os.path.isdir(full) and is_write_target(name):
            excluded.append({"path": name, "reason":
                             "SOLVER WRITE TARGET -- measured: DAFoam rewrites "
                             "0/U (and processor*/0/U) mid-run when the patchV DV "
                             "updates the inlet BC.  Excluded BY NAME so this "
                             "guard asserts no premise the solver falsifies."})
    for sub in input_subdirs:
        base = os.path.join(arm_dir, sub)
        if not os.path.exists(base):
            refuse("MANIFEST_INPUT_ABSENT", {"path": base})
        if os.path.isfile(base):
            entries.append({"path": sub, "md5": md5_of(base)})
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                entries.append({"path": os.path.relpath(full, arm_dir),
                                "md5": md5_of(full)})
    if not entries:
        refuse("MANIFEST_EMPTY",
               {"arm_dir": arm_dir,
                "note": "a manifest resolved by existence has nothing to resolve to"})
    return {"item": ITEM, "entries": sorted(entries, key=lambda e: e["path"]),
            "n_entries": len(entries), "excluded_write_targets": excluded}


def check_manifest(arm_dir, manifest):
    for e in manifest["entries"]:
        full = os.path.join(arm_dir, e["path"])
        if not os.path.isfile(full):
            refuse("MANIFEST_ENTRY_MISSING", {"path": e["path"], "arm_dir": arm_dir})
        got = md5_of(full)
        if got != e["md5"]:
            refuse("MANIFEST_ENTRY_MUTATED",
                   {"path": e["path"], "recorded_md5": e["md5"], "on_disk_md5": got})
    return True


# ============================================================================
# L2 -- rule 4's age assertion, unchanged in strength
# ============================================================================
def check_arm(arm_dir, artefacts, sentinel, manifest, mount_sources):
    """Refuses unless EVERY clause holds.  Returns the evidence dict on success."""
    assert_sentinel_outside_mounts(sentinel, mount_sources)
    if not os.path.isfile(sentinel):
        refuse("AGE_DATUM_ABSENT", {"sentinel": sentinel})
    # FULL-PRECISION DATUM.  This was `int(...)`, which truncated the datum DOWN
    # while artefact mtimes stayed float -- erring PERMISSIVE by up to one second.
    # The supervisor raised it as a docstring mismatch; this lane's own probe
    # showed it was worse than that: a sentinel at 1000.9 with an artefact at
    # 1000.5 -- an artefact GENUINELY OLDER than the launch -- was ACCEPTED.
    # A sub-second window is still a window, and "strictly greater" is what the
    # guard claims.  Fixed rather than documented.  Driven red by RED-6.
    datum = os.stat(sentinel).st_mtime
    check_manifest(arm_dir, manifest)
    seen = []
    for art in artefacts:
        full = os.path.join(arm_dir, art)
        if not os.path.isfile(full):
            refuse("ARTEFACT_ABSENT", {"artefact": art, "arm_dir": arm_dir})
        amt = os.stat(full).st_mtime
        if not amt > datum:                       # STRICTLY greater -- rule 4
            refuse("ARTEFACT_NOT_NEWER_THAN_DATUM",
                   {"artefact": art, "datum": datum, "artefact_mtime": amt,
                    "note": "age guard, CLAUDE.md rule 4; strictly greater, no tolerance"})
        seen.append({"artefact": art, "mtime": amt})
    return {"datum": datum, "sentinel": sentinel, "artefacts": seen,
            "manifest_entries": manifest["n_entries"],
            "excluded_write_targets": [x["path"] for x in manifest["excluded_write_targets"]]}


# ============================================================================
# rule 3 -- the RELATIVE plant, and the reading it is asked to move
# ============================================================================
def plant_relative(d_ref, band_pct, k):
    """plant = K * (band/100) * |d_ref|.  Registered formula; K registered at freeze."""
    return k * (band_pct / 100.0) * abs(d_ref)


def reading_moves_pp(d_ref, plant):
    """The percentage-point move the plant induces in a reading normalised by
    |d_ref| -- i.e. what the gate's band is measured in."""
    return abs(plant) / abs(d_ref) * 100.0


# ============================================================================
# SELFTEST -- every red leg driven RED, every green leg driven GREEN
# ============================================================================
def _touch(path, when, content=b"x"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(content)
    os.utime(path, (when, when))


def _fixture(root, arm="S1"):
    """A staged arm with the exact shape D19's S1 had."""
    d = os.path.join(root, arm)
    T = int(time.time()) - 10000
    for f in ("T", "U", "alphat", "epsilon", "k", "nuTilda", "nut", "omega", "p"):
        _touch(os.path.join(d, "0.orig", f), T, b"internalField uniform (100 0 0);\n")
        _touch(os.path.join(d, "0", f), T, b"internalField uniform (100 0 0);\n")
    _touch(os.path.join(d, "constant", "polyMesh", "boundary"), T, b"boundary\n")
    _touch(os.path.join(d, "system", "controlDict"), T, b"controlDict\n")
    _touch(os.path.join(d, "d19r_xf.py"), T, b"instrument\n")
    return d, T


def _guard_result(arm_dir, artefacts, sentinel, manifest, mounts):
    try:
        check_arm(arm_dir, artefacts, sentinel, manifest, mounts)
        return None
    except Refusal as exc:
        return json.loads(str(exc))["REFUSE"]


INPUT_SUBDIRS = ["0.orig", "constant", "system", "d19r_xf.py"]


def selftest():
    ok = True
    tmp = tempfile.mkdtemp(prefix="d19r_guard_")
    try:
        run_root = os.path.join(tmp, "CURRICULUM-D19R-fixture")
        os.makedirs(run_root)
        mounts = [run_root]                      # exactly `-v "$BASE":/mnt`
        arm_dir, T = _fixture(run_root)
        spath, datum = stamp_sentinel(run_root, "S1", mounts)
        manifest = build_manifest(arm_dir, INPUT_SUBDIRS)

        print("D19R AGE GUARD -- CONTROLS")
        print("  sentinel      : %s" % spath)
        print("  datum epoch   : %.6f  (FULL PRECISION -- not truncated; RED-6)" % datum)
        print("  manifest      : %d input files; write targets excluded by name: %s"
              % (manifest["n_entries"],
                 [x["path"] for x in manifest["excluded_write_targets"]]))
        print()

        def leg(name, want, got, extra=""):
            nonlocal ok
            good = (got == want)
            ok = ok and good
            print("  %-9s %-46s expect=%-28s got=%-28s %s%s"
                  % (name, "", str(want), str(got), "OK" if good else "**LEG DID NOT FIRE**",
                     (" " + extra) if extra else ""))
            return good

        art = "d19r_S1.json"

        # GREEN-2 clean
        _touch(os.path.join(arm_dir, art), datum + 5, b"{}")
        leg("GREEN-2", None, _guard_result(arm_dir, [art], spath, manifest, mounts))

        # RED-1 stale artefact (the answer inherited from a previous run)
        _touch(os.path.join(arm_dir, art), datum - 10, b"{}")
        leg("RED-1", "ARTEFACT_NOT_NEWER_THAN_DATUM",
            _guard_result(arm_dir, [art], spath, manifest, mounts),
            "(planted stale answer, 10 s older than launch)")

        # RED-2 equal mtime -- strictly greater, not >=
        _touch(os.path.join(arm_dir, art), datum, b"{}")
        leg("RED-2", "ARTEFACT_NOT_NEWER_THAN_DATUM",
            _guard_result(arm_dir, [art], spath, manifest, mounts),
            "(mtime EQUAL to datum)")

        # GREEN-1 THE D19 REGRESSION -- the exact false refusal must not recur:
        #   0/T replaced by 0/T.gz, 0/U rewritten AFTER the sentinel, artefact newer.
        _touch(os.path.join(arm_dir, art), datum + 40, b"{}")
        for f in ("T", "U", "p", "nut", "nuTilda", "alphat"):
            os.remove(os.path.join(arm_dir, "0", f))
            _touch(os.path.join(arm_dir, "0", f + ".gz"), datum + 30,
                   b"internalField nonuniform List<vector>\n")
        os.utime(os.path.join(arm_dir, "0", "U.gz"), (datum + 35, datum + 35))
        leg("GREEN-1", None, _guard_result(arm_dir, [art], spath, manifest, mounts),
            "(D19's exact false refusal -- 0/ rewritten mid-run)")

        # RED-3 a manifest INPUT mutated (count unchanged -- D19's count check
        # would have missed this; this one does not)
        n_before = len(os.listdir(os.path.join(arm_dir, "0.orig")))
        _touch(os.path.join(arm_dir, "0.orig", "T"), T, b"TAMPERED\n")
        n_after = len(os.listdir(os.path.join(arm_dir, "0.orig")))
        leg("RED-3", "MANIFEST_ENTRY_MUTATED",
            _guard_result(arm_dir, [art], spath, manifest, mounts),
            "(file count unchanged %d->%d -- a count is not an identity)" % (n_before, n_after))
        _touch(os.path.join(arm_dir, "0.orig", "T"), T, b"internalField uniform (100 0 0);\n")

        # RED-5 manifest entry removed
        os.remove(os.path.join(arm_dir, "system", "controlDict"))
        leg("RED-5", "MANIFEST_ENTRY_MISSING",
            _guard_result(arm_dir, [art], spath, manifest, mounts))
        _touch(os.path.join(arm_dir, "system", "controlDict"), T, b"controlDict\n")

        # RED-4 sentinel inside the mount source -- L1's structural claim has teeth
        got = None
        try:
            assert_sentinel_outside_mounts(os.path.join(run_root, "S1", ".datum"), mounts)
        except Refusal as exc:
            got = json.loads(str(exc))["REFUSE"]
        leg("RED-4", "AGE_DATUM_INSIDE_MOUNT", got,
            "(a datum the solve could write is refused AT LAUNCH)")

        # RED-6  SUB-SECOND STALE ARTEFACT.  Regression leg for the truncated
        # datum: sentinel at T+0.9, artefact at T+0.5 -- the artefact is GENUINELY
        # OLDER than the launch.  Under `int(datum)` this was ACCEPTED (measured).
        base = int(datum) + 100
        os.utime(spath, (base + 0.9, base + 0.9))
        _touch(os.path.join(arm_dir, art), base + 0.5, b"{}")
        leg("RED-6", "ARTEFACT_NOT_NEWER_THAN_DATUM",
            _guard_result(arm_dir, [art], spath, manifest, mounts),
            "(artefact 0.4 s OLDER than launch -- the truncation window)")
        os.utime(spath, (datum, datum))
        _touch(os.path.join(arm_dir, art), datum + 40, b"{}")

        # RED-7  THE MANIFEST MAY NOT PIN A SOLVER WRITE TARGET.  The exclusion is
        # ENFORCING, not descriptive.  This leg is the one the original selftest
        # STRUCTURALLY COULD NOT SEE, because it only ever passed a correct
        # `input_subdirs` -- a fixture authored from the consumer's expectations is
        # a tautology on shape.  Found by the supervisor's adversarial probe.
        got7 = None
        try:
            build_manifest(arm_dir, ["0", "system"])
        except Refusal as exc:
            got7 = json.loads(str(exc))["REFUSE"]
        leg("RED-7", "MANIFEST_INPUT_IS_WRITE_TARGET", got7,
            "(caller pins 0/ -- REFUSED, not silently filtered)")
        got7b = None
        try:
            build_manifest(arm_dir, ["processor0"])
        except Refusal as exc:
            got7b = json.loads(str(exc))["REFUSE"]
        leg("RED-7b", "MANIFEST_INPUT_IS_WRITE_TARGET", got7b,
            "(processor* is a write target too)")

        # ---- rule 3: the RELATIVE plant, both legs --------------------------
        print()
        print("D19R PLANTED CONTROL -- RELATIVE, K REGISTERED AT FREEZE")
        band = 10.0                       # G19R-1b's band
        d_ref = -2.065253e-04             # D19's measured shape[7]/CD FD at 1e-3
        p_ok = plant_relative(d_ref, band, PLANT_K)
        m_ok = reading_moves_pp(d_ref, p_ok)
        p_sh = plant_relative(d_ref, band, PLANT_K_SHRUNK)
        m_sh = reading_moves_pp(d_ref, p_sh)
        print("  formula     plant_i = K * (band/100) * |d_ref_i|      band = %.1f %%" % band)
        print("  d_ref       %.6e   (D19 measured shape[7]/CD FD at 1e-3)" % d_ref)
        print("  K = %.1f     plant %.6e -> reading moves %.4f pp   band %.1f pp  -> %s"
              % (PLANT_K, p_ok, m_ok, band, "CROSSES" if m_ok > band else "DOES NOT CROSS"))
        print("  K = %.1f     plant %.6e -> reading moves %.4f pp   band %.1f pp  -> %s"
              % (PLANT_K_SHRUNK, p_sh, m_sh, band, "CROSSES" if m_sh > band else "DOES NOT CROSS"))
        suff = m_ok > band
        red = not (m_sh > band)
        ok = ok and suff and red
        print("  SUFFICIENCY  (K=%.1f must cross)      : %s" % (PLANT_K, "OK" if suff else "**FAILED**"))
        print("  SUFFICIENCY RED LEG (K=%.1f must NOT) : %s" % (PLANT_K_SHRUNK, "OK -- DROVE RED" if red else "**DID NOT DRIVE RED**"))
        print("  (SO-2M was lost to an absolute plant that was 2.48 %% of its own")
        print("   reference and could not cross its own 5 %% band.  This one is sized")
        print("   to the band by construction, and the shrunken leg proves the reader")
        print("   is measuring CROSSING rather than always answering yes.)")

        print()
        print("D19R AGE GUARD SELFTEST: %s" % ("OK -- every red leg fired, both green legs passed"
                                               if ok else "FAILED"))
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.stderr.write(__doc__.strip().splitlines()[0] + "\nUsage: d19r_age_guard.py --selftest\n")
    sys.exit(64)
