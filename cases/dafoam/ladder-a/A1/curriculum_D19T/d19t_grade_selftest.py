#!/usr/bin/env python3
r"""Curriculum D19T -- THE GRADER SELFTEST.

Every gate is driven RED on a synthetic fixture, and the two structural repairs
this item claims are driven as their own legs:

  * `RED-CEIL`  -- the ITEM-LEVEL CEILING ACTUALLY BINDS.  D19M composes the
    item from `rows[r]["verdict"]`, which `compose_row` has already capped, so
    the item's `_apply_ceiling` receives a token that cannot exceed the ceiling
    and `capped_by_ceiling` is ALWAYS `false` at item level.  This leg runs BOTH
    compositions on ONE fixture and requires them to DISAGREE.

  * `RED-TOL-*` -- the load-bearing tolerance gate fails closed on an empty
    reading, on a wrong tolerance, and on a short count.

**THE FIXTURE VALUES ARE SYNTHETIC WHERE THEY ARE SHAPED AND LANDED WHERE THEY
ARE QUOTED.**  T08's `shape[7]` numbers are D19R's OWN measured values from
`.../CURRICULUM-D19R-.../S8/d19r_S.json`; the T10 and T12 numbers are
CONSTRUCTED to the shape H1 predicts.  This selftest therefore proves the
LOGIC AND THE CONTROLS.  **It proves nothing whatever about the physics**, and
a green selftest is not a green run.
"""
import json
import os
import shutil
import time
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d19t_grade as G                                             # noqa: E402
import d19t_age_guard as AGE                                       # noqa: E402

ADJ7 = -2.099480e-04
ADJ6 = -1.413381e-02
CPUSET, DIGEST, SO_MD5 = "1,15", "sha256:deadbeef", "85f59e87253e0a71a813f64ca6e4c425"

# D19R's LANDED shape[7]/CD -- quoted, not invented
T08_S7 = {3.0e-2: -0.00014732049854471185, 1.0e-2: -0.00020890917339921877,
          1.0e-3: -0.00020648832854686106, 1.0e-4: -0.00016300047367412418,
          1.0e-5: 0.000251917448013117}
T08_S6 = {3.0e-2: -0.008726230668498758, 1.0e-2: -0.013661913516216373,
          1.0e-3: -0.014133126405191376, 1.0e-4: -0.014182212719759946,
          1.0e-5: -0.014422999744523322}
# CONSTRUCTED to H1's predicted shape: truncation untouched at 3e-2, bias gone below
_F = {3.0e-2: 1.2983, 1.0e-2: 1.005, 1.0e-3: 1.001, 1.0e-4: 1.0005, 1.0e-5: 1.002}
T10_S7 = {s: ADJ7 * f for s, f in _F.items()}
T12_S7 = {s: ADJ7 * (1.0 + (f - 1.0) * 0.5 if s != 3.0e-2 else f) for s, f in _F.items()}
T12_S7[3.0e-2] = ADJ7 * 1.2983


def fd_block(vals, cl_scale=1.0):
    return {repr(s): {"step": s, "dCD": repr(v), "dCL": repr(0.4888695 * cl_scale),
                      "CD_plus": repr(0.0146), "CD_minus": repr(0.0146), "ok": True,
                      "is_trivial_baseline": bool(s == G.TRIVIAL_STEP)}
            for s, v in vals.items()}


def t_doc(tol, s7, s6):
    return {"item": "D19T", "mode": "T", "nprocs": 2,
            "identity": {"libidwarp_so_md5": SO_MD5},
            "primalMinResTol_requested": tol, "primalMinResTol_in_namespace": tol,
            "contains_adjoint": False, "grades_nothing": False,
            "rows": [{"dv": "shape", "idx": 7, "status": "MEASURED",
                      "graded": True, "fd": fd_block(s7)},
                     {"dv": "shape", "idx": 6, "status": "MEASURED",
                      "graded": False, "fd": fd_block(s6, 1.001)}]}


def x_doc():
    return {"item": "D19T", "mode": "X", "nprocs": 2,
            "identity": {"libidwarp_so_md5": SO_MD5}, "contains_adjoint": True,
            "primalMinResTol_requested": 1.0e-10,
            "adjoint": {"CD": {"shape": ["0.0"] * 6 + [repr(ADJ6), repr(ADJ7)],
                               "patchV": ["0.0", "0.0"]},
                        "CL": {"shape": ["0.0"] * 6 + ["-0.2551356", "0.4888695"],
                               "patchV": ["0.0", "0.0"]}}}


N_SOLVES = 2 * len(G.STEPS) * 2 + 2      # 22


def tol_log(tol, n, terminal):
    body = "".join("Minimal residual %.4e satisfied the prescribed tolerance %g\n"
                   % (0.97 * tol, tol) for _ in range(n))
    return "Time = 1\n" + body + terminal + "\nEnd\n"


def build(root):
    """A fixture whose every gate is GREEN, so each red leg changes ONE thing."""
    os.makedirs(root, exist_ok=True)
    caps = G.ARM_CAP_CORE_MIN
    led = []
    for arm in G.ARMS_DECLARED:
        led.append("ARM=%s ROW=PATCHED IMG=img DIGEST=%s rc=0 wall_s=30 ranks=%d "
                   "core_min=%.3f cap_core_min=%.1f memory=4g cpuset=%s"
                   % (arm, DIGEST, G.ARM_RANKS[arm], caps[arm] * 0.4, caps[arm], CPUSET))
    with open(os.path.join(root, "ledger.txt"), "w") as fh:
        fh.write("\n".join(led) + "\n")

    docs = {"T08": t_doc(1e-8, T08_S7, T08_S6), "T10": t_doc(1e-10, T10_S7, T08_S6),
            "T12": t_doc(1e-12, T12_S7, T08_S6), "XT10": x_doc()}
    for arm in G.ARMS_DECLARED:
        d = os.path.join(root, arm)
        os.makedirs(os.path.join(d, "system"), exist_ok=True)
        with open(os.path.join(d, "system", "controlDict"), "w") as fh:
            fh.write("endTime 1000;\n")
        # a manifest that HOLDS -- the pre-normalisation premise -- built BEFORE
        # the sentinel, exactly as the launcher does it
        man = AGE.build_manifest(d, ["system"])
        with open(os.path.join(d, ".d19t_manifest.json"), "w") as fh:
            json.dump(man, fh)
        # THE AGE DATUM: stamped after staging and BEFORE the artefacts, so the
        # artefacts are strictly newer.  This is rule 4's age guard, and the
        # fixture has to honour it or the green leg is not green.
        AGE.stamp_sentinel(root, arm, [root])
        time.sleep(0.02)
        kind = G.ARM_KIND[arm]
        if kind == "SCRIPT":
            with open(os.path.join(d, "checkMesh.log"), "w") as fh:
                fh.write("cells: 4032\n")
            with open(os.path.join(root, "%s_20260901T000000Z_1.log" % arm), "w") as fh:
                fh.write("checkMesh\ncells: 4032\n%s\nEnd\n" % G.TERMINAL["SCRIPT"])
        else:
            with open(os.path.join(d, G.ARTEFACT[kind]), "w") as fh:
                json.dump(docs[arm], fh)
            n = N_SOLVES if kind == "T" else 1
            with open(os.path.join(root, "%s_20260901T000000Z_1.log" % arm), "w") as fh:
                fh.write(tol_log(G.ARM_TOL[arm], n, G.TERMINAL[kind]))
    return root


def run(root):
    return G.grade(root, CPUSET, DIGEST, SO_MD5)


def d19m_style_item(gates, rows):
    """D19M's composition, reproduced EXACTLY: the item reads the CAPPED token."""
    row_capped = [rows[r]["verdict"] for r in rows]          # <-- the defect
    raw = G._worst(row_capped)
    verdict, capped = G._apply_ceiling(raw)
    return {"verdict": verdict, "verdict_before_ceiling": raw, "capped_by_ceiling": capped}


def main():
    ok = True
    print("D19T GRADER SELFTEST -- logic and controls only; the physics is not in here")
    print()

    td = tempfile.mkdtemp(prefix="d19t_selftest_")
    try:
        # ---------------- GREEN ------------------------------------------
        root = build(os.path.join(td, "green"))
        out = run(root)
        green_ok = (out["verdict_before_ceiling"] == "PASS"
                    and out["verdict"] == "GATE REACHED"
                    and out["capped_by_ceiling"] is True
                    and out["birth_register"]["n_not_born"] == 0)
        ok = ok and green_ok
        print("GREEN  every gate passes -> uncapped %-12s capped %-12s ceiling bound=%s  %s"
              % (out["verdict_before_ceiling"], out["verdict"],
                 out["capped_by_ceiling"], "OK" if green_ok else "**WRONG**"))
        print("       birth register: %d/%d readers born, %d zero-legs proved"
              % (out["birth_register"]["n_born"], out["birth_register"]["n_readers"],
                 out["birth_register"]["n_readers"]
                 - out["birth_register"]["n_zero_leg_unproved"]))
        print("       plateau T08 %-10s T10 %-10s T12 %-10s"
              % (out["gates"]["G-PLAT7"]["T08"]["verdict"],
                 out["gates"]["G-PLAT7"]["T10"]["verdict"],
                 out["gates"]["G-PLAT7"]["T12"]["verdict"]))
        print("       G-EPS ratio %.1fx (required %.1fx) -> %s"
              % (out["gates"]["G-EPS"]["ratio_1e8_over_1e10"],
                 out["gates"]["G-EPS"]["ratio_required"],
                 out["gates"]["G-EPS"]["verdict"]))

        # ---------------- RED-CEIL: the two compositions must DISAGREE -----
        mine = {k: out[k] for k in ("verdict", "verdict_before_ceiling", "capped_by_ceiling")}
        theirs = d19m_style_item(out["gates"], out["rows"])
        disagree = (mine["capped_by_ceiling"] is True
                    and theirs["capped_by_ceiling"] is False
                    and mine["verdict"] == theirs["verdict"])
        ok = ok and disagree
        print()
        print("RED-CEIL  the item-level ceiling must ACTUALLY BIND")
        print("   D19T  (from verdict_before_ceiling): uncapped %-6s capped_by_ceiling=%s"
              % (mine["verdict_before_ceiling"], mine["capped_by_ceiling"]))
        print("   D19M  (from the already-capped token): uncapped %-6s capped_by_ceiling=%s"
              % (theirs["verdict_before_ceiling"], theirs["capped_by_ceiling"]))
        print("   -> the two DISAGREE on whether the ceiling bound: %s"
              % ("OK -- the repair is live and measurable" if disagree else "**WRONG**"))

        # ---------------- the RED legs ------------------------------------
        legs = []

        def leg(name, mutate, check, note):
            r = os.path.join(td, name)
            build(r)
            mutate(r)
            try:
                o = run(r)
                got, why = check(o)
            except G.Refusal as exc:
                got, why = check_refusal(exc)
            legs.append((name, got, note, why))

        def check_refusal(exc):
            return "REFUSED", json.loads(str(exc))["REFUSE"]

        def wlog(r, arm, text):
            with open(os.path.join(r, "%s_20260901T000000Z_1.log" % arm), "w") as fh:
                fh.write(text)

        def wdoc(r, arm, doc):
            with open(os.path.join(r, arm, G.ARTEFACT[G.ARM_KIND[arm]]), "w") as fh:
                json.dump(doc, fh)

        leg("RED-TOL-ZERO",
            lambda r: wlog(r, "T10", "Time = 1\n%s\nEnd\n" % G.TERMINAL["T"]),
            lambda o: (o["gates"]["G-TOL"]["T10"]["verdict"], o["verdict"]),
            "a log with NO tolerance statement must fail CLOSED (NOT A RESULT)")

        leg("RED-TOL-WRONG",
            lambda r: wlog(r, "T10", tol_log(1e-8, N_SOLVES, G.TERMINAL["T"])),
            lambda o: (o["gates"]["G-TOL"]["T10"]["verdict"], o["verdict"]),
            "T10 honouring 1e-8 = the dictionary did not take (GATE FAIL)")

        leg("RED-TOL-SHORT",
            lambda r: wlog(r, "T10", tol_log(1e-10, N_SOLVES - 1, G.TERMINAL["T"])),
            lambda o: (o["gates"]["G-TOL"]["T10"]["verdict"], o["verdict"]),
            "one solve short = a solve ran out of iterations (GATE FAIL)")

        def bad_plateau(r):
            bad = dict(T10_S7)
            bad[1.0e-4] = ADJ7 * 1.9          # fine side 90 % off the centre
            wdoc(r, "T10", t_doc(1e-10, bad, T08_S6))
        leg("RED-PLAT", bad_plateau,
            lambda o: (o["gates"]["G-PLAT7"]["T10"]["verdict"], o["verdict"]),
            "a plateau that does not close two-sided (GATE FAIL)")

        def bad_repro(r):
            bad = {s: v * 3.0 for s, v in T08_S7.items()}
            wdoc(r, "T08", t_doc(1e-8, bad, T08_S6))
        leg("RED-REPRO", bad_repro,
            lambda o: (o["gates"]["G-REPRO"]["verdict"], o["verdict"]),
            "T08 not reproducing D19R = this is not D19R's instrument (GATE FAIL)")

        def bad_trivial(r):
            good = dict(T10_S7)
            good[G.TRIVIAL_STEP] = ADJ7 * 1.001    # the WRONG step now agrees
            wdoc(r, "T10", t_doc(1e-10, good, T08_S6))
        leg("RED-TRIVIAL", bad_trivial,
            lambda o: (o["gates"]["G-TRIVIAL"]["verdict"], o["verdict"]),
            "charter section 4: the wrong step agreeing WITHDRAWS G-ADJ (item NOT A RESULT)")

        def bad_eps(r):
            wdoc(r, "T10", t_doc(1e-10, T08_S7, T08_S6))   # eps unchanged from T08
        leg("RED-EPS", bad_eps,
            lambda o: (o["gates"]["G-EPS"]["verdict"], o["verdict"]),
            "eps NOT falling with the tolerance falsifies H1 (GATE FAIL)")

        def over_cap(r):
            t = open(os.path.join(r, "ledger.txt")).read().replace(
                "core_min=1.600", "core_min=9.900")
            open(os.path.join(r, "ledger.txt"), "w").write(t)
        leg("RED-CAP", over_cap,
            lambda o: (o["gates"]["G-CAPS"]["verdict"], o["verdict"]),
            "an arm over its registered cap (GATE FAIL)")

        def wrong_np(r):
            t = open(os.path.join(r, "ledger.txt")).read().replace(
                "ARM=T10 ROW=PATCHED IMG=img DIGEST=%s rc=0 wall_s=30 ranks=2" % DIGEST,
                "ARM=T10 ROW=PATCHED IMG=img DIGEST=%s rc=0 wall_s=30 ranks=4" % DIGEST)
            open(os.path.join(r, "ledger.txt"), "w").write(t)
        leg("RED-NP", wrong_np,
            lambda o: (o["gates"]["G-NP"]["verdict"], o["verdict"]),
            "np off the registered value confounds the tolerance (GATE FAIL)")

        def mutate_manifest(r):
            with open(os.path.join(r, "T10", "system", "controlDict"), "a") as fh:
                fh.write("kahipCoeffs { config fast; }\n")
        leg("RED-MANIFEST", mutate_manifest,
            lambda o: (o["gates"]["G-MANIFEST"]["verdict"], o["verdict"]),
            "an input mutated under the run -- the D19R2 blocker, reachable here")

        def drop_arm(r):
            t = "\n".join(l for l in open(os.path.join(r, "ledger.txt")).read().splitlines()
                          if not l.startswith("ARM=T12"))
            open(os.path.join(r, "ledger.txt"), "w").write(t + "\n")
        leg("RED-STAGES", drop_arm,
            lambda o: (o["gates"]["G-STAGES"]["verdict"], o["verdict"]),
            "declared 5 arms, ran 4 (NOT A RESULT)")

        def fatal(r):
            wlog(r, "T10", tol_log(1e-10, N_SOLVES, G.TERMINAL["T"]) + "\nMPI_ABORT\n")
        leg("RED-FATAL", fatal,
            lambda o: (o["gates"]["G-COMPLETE"]["T10"]["verdict"], o["verdict"]),
            "a fatal token in the log (GATE FAIL)")

        print()
        print("RED LEGS -- each changes exactly ONE thing on the green fixture")
        want = {"RED-TOL-ZERO": "NOT A RESULT", "RED-TOL-WRONG": "GATE FAIL",
                "RED-TOL-SHORT": "GATE FAIL", "RED-PLAT": "GATE FAIL",
                "RED-REPRO": "GATE FAIL", "RED-TRIVIAL": "GATE FAIL",
                "RED-EPS": "GATE FAIL", "RED-CAP": "GATE FAIL", "RED-NP": "GATE FAIL",
                "RED-MANIFEST": "GATE FAIL", "RED-STAGES": "NOT A RESULT",
                "RED-FATAL": "GATE FAIL"}
        for name, got, note, item_v in legs:
            good = got == want[name]
            ok = ok and good
            print("   %-14s gate=%-13s item=%-13s %-5s  %s"
                  % (name, got, item_v, "OK" if good else "**WRONG**", note))

        # ---------------- the birth register must REFUSE when blinded -----
        print()
        print("RED-BIRTH -- a blinded reader must REFUSE the whole grading, not degrade it")
        real = G.read_tolerance_lines
        G.read_tolerance_lines = lambda text: []
        try:
            run(build(os.path.join(td, "blind")))
            got = "GRADED ANYWAY"
        except G.Refusal as exc:
            got = json.loads(str(exc))["REFUSE"]
        finally:
            G.read_tolerance_lines = real
        good = got == "CONTROL_READER_NOT_BORN"
        ok = ok and good
        print("   R3 blinded (always returns []) -> %-28s %s"
              % (got, "OK" if good else "**WRONG**"))

        # ---------------- L-332: asserts are counted, and the counter is born
        print()
        n_here = G.count_asserts(os.path.abspath(G.__file__))
        planted = os.path.join(td, "planted_assert.py")
        shutil.copy(os.path.abspath(G.__file__), planted)
        with open(planted, "a") as fh:
            fh.write("\nassert True  # planted\n")
        n_planted = G.count_asserts(planted)
        good = n_planted == n_here + 1
        ok = ok and good
        print("L-332  assert counter: grader has %d, planted copy has %d  %s"
              % (n_here, n_planted, "OK -- the counter is born" if good else "**WRONG**"))

    finally:
        shutil.rmtree(td, ignore_errors=True)

    print()
    print("D19T GRADER SELFTEST %s" % ("OK" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
