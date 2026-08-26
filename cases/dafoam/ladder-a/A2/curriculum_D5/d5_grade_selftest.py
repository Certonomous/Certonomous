#!/usr/bin/env python3
"""Selftest for d5_grade.py.  Run under BOTH `python3` and `python3 -O`; every
refusal below must STILL FIRE under -O (QUEUE_ENTRY_STANDARD section 5 rule 2).
Fixtures live under a scratch directory passed as argv[1]; nothing here touches
the registered run root, D4's run root, or docker.  Each guard is shown to be
the one credited: after each positive fixture the owning constant is mutated
and the control must flip (rule 3 / section 5 rule 5).
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d5_grade as G   # noqa: E402

PASS = 0
FAIL = 0


def ok(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [OK ] %s %s" % (name, extra))
    else:
        FAIL += 1
        print("  [BAD] %s %s" % (name, extra))


def refused(fn, *a, **k):
    try:
        fn(*a, **k)
    except G.Refuse as exc:
        return True, str(exc)
    return False, None


ROW = ("ARM={arm} ROW=PATCHED IMG=dafoam-idwarp-rot:v1 DIGEST={dig} rc={rc} wall_s={wall} "
       "ranks=4 core_min={cm} cap_core_min={cap} enforced_wall_s=12000 enforced_core_min={cap} "
       "memory=12g inspect(exit,oomkilled)=[{ke} {oom}] memavail_pre_GiB={mpre} memavail_post_GiB={mpost} "
       "cpuset={cs} delivered_cores_mean=[{dl}] siblings_pre=[] siblings_post=[] log={log}\n")


def row(arm, rc=0, ke=None, oom="false", cm=1.0, cap=None, mpre="20.00", mpost="20.00",
        dl="3.9900 n=10 max_nr_throttled=0", log=None, cs=G.CPUSET_REGISTERED, dig=G.IMG_PATCHED_DIGEST,
        wall=60):
    return ROW.format(arm=arm, rc=rc, ke=(rc if ke is None else ke), oom=oom, cm=cm,
                      cap=(G.CAPS[arm] if cap is None else cap), mpre=mpre, mpost=mpost, dl=dl,
                      log=(log or "%s_x.log" % arm), cs=cs, dig=dig, wall=wall)


IPOPT_TMPL = ("Number of Iterations....: {n}\n\n"
              "                                   (scaled)                 (unscaled)\n"
              "Objective...............:   {v:.16e}    {v:.16e}\n\n{exit}\n")


def write_ipopt(path, v, n=80, exit_="EXIT: Optimal Solution Found."):
    open(path, "w").write(IPOPT_TMPL.format(n=n, v=v, exit=exit_))


def write_fd(path, flips=0, near_zero=0, rel=1.0):
    rows = []
    for i, (dv, idx) in enumerate(G.COMPONENTS_REGISTERED):
        if i < near_zero:
            rows.append({"dv": dv, "idx": idx, "status": "NEAR_ZERO", "fd": {}})
            continue
        j = 1.0e-3 * (i + 1)
        d = j * (1.0 + rel / 100.0)
        if i < near_zero + flips:
            d = -d
        rows.append({"dv": dv, "idx": idx, "status": "PLANNED", "s_lo": 1e-3, "s_hi": 3e-3,
                     "J_adj": repr(j), "fd": {"s_lo": {"ok": True, "d": repr(d * 1.001)},
                                               "s_hi": {"ok": True, "d": repr(d)}}})
    json.dump({"components_requested": G.COMPONENTS_REGISTERED, "rows": rows}, open(path, "w"))


def build_base(root, cd48, cd192, cd96, flips48=0, flips192=0, rc=None, terminal_last=True,
               acc_ok=True, stale=False, cm=None):
    """A complete, clean run root with every arm's row, logs, artefacts, datums."""
    if os.path.isdir(root):
        shutil.rmtree(root)
    os.makedirs(root)
    d4o = os.path.join(root, "D4_O")
    os.makedirs(d4o)
    write_ipopt(os.path.join(d4o, "opt_IPOPT.txt"), cd96)
    datum = int(time.time()) - 100
    led = open(os.path.join(root, "ledger.txt"), "w")
    led.write("ITEM=D5 staged=fixture\n")
    for arm in G.ARMS_REQUIRED:
        adir = os.path.join(root, G.ARM_DIR[arm])
        os.makedirs(os.path.join(adir, "0"), exist_ok=True)
        u = os.path.join(adir, "0", "U")
        open(u, "w").write("U\n")
        os.utime(u, (datum, datum))
        open(os.path.join(adir, ".d4_age_datum"), "w").write(str(datum))
        log = "%s_fix.log" % arm
        body = "start\nD4S_IDWARP_SO_MD5: %s\nFinalising parallel run\n" % G.IDWARP_SO_MD5_PATCHED
        if not terminal_last and arm.startswith("O"):
            body += "mpirun detected abort\n"
        open(os.path.join(root, log), "w").write(body)
        if not (arm.startswith("ACC") and not acc_ok):
            open(os.path.join(root, log + ".ok.fix"), "w").write("")
        a_rc = rc.get(arm, 0) if isinstance(rc, dict) else 0
        a_cm = (cm or {}).get(arm, G.PREDICTED_CORE_MIN[arm])
        led.write(row(arm, rc=a_rc, cm=a_cm, log=log))
    led.close()
    for d, arm, cd, fl in (("48", "O48", cd48, flips48), ("192", "O192", cd192, flips192)):
        adir = os.path.join(root, arm)
        write_ipopt(os.path.join(adir, "opt_IPOPT.txt"), cd)
        open(os.path.join(adir, "OptView.hst"), "w").write("h")
        open(os.path.join(adir, "d4_endpoint_dvs.json"), "w").write("{}")
        write_fd(os.path.join(adir, "d5_fd_endpoint.json"), flips=fl)
    now = time.time()
    for dp, dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            if not (f == "U" and os.path.basename(dp) == "0"):
                os.utime(p, (now, now))
    if stale:
        for arm in ("O48",):
            p = os.path.join(root, arm, "opt_IPOPT.txt")
            os.utime(p, (datum - 5, datum - 5))
    return d4o


def main():
    scratch = sys.argv[1]
    os.makedirs(scratch, exist_ok=True)
    mode = "python3 -O" if not __debug__ else "python3"
    print("D5 GRADE SELFTEST under %s  grader_md5=%s" % (mode, G.md5_of(G.__file__)))

    # ---- L-332: AST count sees zero in the grader and one planted ----
    r = G.self_assert_check()
    ok("L-332 grader carries 0 assert nodes and the counter sees a planted one",
       r["assert_nodes"] == 0 and r["counter_sees_planted"] == 1, str(r))

    # ---- ledger parsing: absent infra -> NOT_MEASURED; garbage -> REFUSE; absent physics -> REFUSE
    p = os.path.join(scratch, "led_nm.txt")
    open(p, "w").write(row("O48", mpre="NOT_MEASURED", mpost="NOT_MEASURED", dl="NOT_MEASURED"))
    rows = G.read_ledger(p)
    ok("absent/NOT_MEASURED infrastructure fields parse to None and are DISCLOSED",
       rows[0]["memavail_pre_GiB"] is None and "delivered" in rows[0]["infra_not_measured"]
       and "memavail_pre_GiB" in rows[0]["infra_not_measured"], str(rows[0]["infra_not_measured"]))
    p = os.path.join(scratch, "led_absent_infra.txt")
    line = row("O48")
    line = line.replace(" memavail_pre_GiB=20.00 memavail_post_GiB=20.00", "")
    open(p, "w").write(line)
    rows = G.read_ledger(p)
    ok("infrastructure fields ENTIRELY ABSENT from the row -> parse, NOT_MEASURED named",
       rows[0]["memavail_post_GiB"] is None and "memavail_post_GiB" in rows[0]["infra_not_measured"])
    p = os.path.join(scratch, "led_garbage.txt")
    open(p, "w").write(row("O48", mpre="abc"))
    rf, msg = refused(G.read_ledger, p)
    ok("PRESENT-BUT-GARBAGE infrastructure value -> REFUSE (absent != garbage)", rf and "row_unparseable" in msg)
    p = os.path.join(scratch, "led_nophys.txt")
    open(p, "w").write(row("O48").replace(" rc=0", ""))
    rf, msg = refused(G.read_ledger, p)
    ok("absent PHYSICS field (rc) -> REFUSE", rf and "row_unparseable" in msg)
    p = os.path.join(scratch, "led_absent.txt")
    rf, msg = refused(G.read_ledger, p)
    ok("absent ledger -> REFUSE", rf and "absent" in msg)

    # ---- CLEAN CONTROL: a complete root grades PASS ----
    root = os.path.join(scratch, "root_clean")
    d4o = build_base(root, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED)
    res = G.grade(root, d4o)
    ok("CLEAN CONTROL -> item PASS, G1 PASS, G-D5-1 PASS (delta_192=-2.6e-4 in band)",
       res["verdict"] == "PASS" and res["gates"]["G1_completion"] == "PASS" and res["gates"]["G-D5-1"] == "PASS",
       json.dumps(res["gates"], sort_keys=True))
    ok("planted-zero control fired on the D4 reference reader (seen_delta == PLANT)",
       abs(res["G-D5-1"]["planted_control"]["seen_delta"] - G.PLANT) < 1e-12)
    ok("P1 HIT, P2 HIT, P3 HIT, P5 HIT on the clean fixture",
       res["predictions"]["P1"]["score"] == "HIT" and res["predictions"]["P2"]["score"] == "HIT"
       and res["predictions"]["P3"]["score"] == "HIT" and res["predictions"]["P5"]["score"] == "HIT",
       json.dumps({k: (v.get("score") if isinstance(v, dict) and "score" in v else "-") for k, v in res["predictions"].items()}))

    # ---- G-D5-1 out of band -> GATE FAIL; then the band is mutated and the control flips ----
    root2 = os.path.join(scratch, "root_oob")
    d4o = build_base(root2, cd48=2.13e-2, cd192=2.06e-2, cd96=G.CD_F_96_RECORDED)
    res = G.grade(root2, d4o)
    ok("DeltaCD(192) = -5.3e-4 outside 3.0e-4 -> G-D5-1 GATE FAIL, item GATE FAIL",
       res["gates"]["G-D5-1"] == "GATE FAIL" and res["verdict"] == "GATE FAIL")
    saved = G.CROSS_BAND_192
    G.CROSS_BAND_192 = 1.0
    gx = G.g_cross_density(root2, d4o, band=G.CROSS_BAND_192)
    G.CROSS_BAND_192 = saved
    ok("GUARD MUTATION: band widened to 1.0 -> the same fixture reads PASS (the refusal came from the band)",
       gx["verdict"] == "PASS")

    # ---- blind reader -> PLANTED_ZERO refuses ----
    def blind(path, where="x"):
        return {"objective": G.CD_F_96_RECORDED, "exit": "EXIT: Optimal Solution Found.", "n_iter": 80,
                "optimal": True, "objective_scaled": 0.0, "path": path}
    rf, msg = refused(G.planted_zero_control, os.path.join(d4o, "opt_IPOPT.txt"),
                      os.path.join(scratch, "ctrl"), reader=blind)
    ok("a reader that cannot see the plant -> REFUSE (rule 3)", rf and "reader_blind" in msg)

    # ---- D4 reference changed on disk -> REFUSE ----
    root3 = os.path.join(scratch, "root_refmoved")
    d4o = build_base(root3, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED + 1e-6)
    rf, msg = refused(G.grade, root3, d4o)
    ok("D4's O/opt_IPOPT.txt objective differs from the recorded CD_f(96) -> REFUSE", rf and "d4_reference_changed" in msg)

    # ---- completion: kernel rc 1 on a SOLVER arm -> NOT A RESULT ----
    root4 = os.path.join(scratch, "root_rc1")
    d4o = build_base(root4, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED, rc={"O192": 1})
    res = G.grade(root4, d4o)
    ok("kernel exit 1 on O192 -> G1 NOT A RESULT, item NOT A RESULT",
       res["gates"]["G1_completion"] == "NOT A RESULT" and res["verdict"] == "NOT A RESULT"
       and res["G1"]["rc_failures"][0]["arm"] == "O192")
    # harness/kernel disagreement -> REFUSE
    p = os.path.join(root4, "ledger.txt")
    txt = open(p).read().replace("rc=1 ", "rc=0 ", 1)
    open(p, "w").write(txt)
    rf, msg = refused(G.grade, root4, d4o)
    ok("harness rc=0 vs kernel exit 1 -> REFUSE (neither chosen silently)", rf and "rc_disagreement" in msg)

    # ---- SOLVER terminal statement not LAST -> NOT A RESULT ----
    root5 = os.path.join(scratch, "root_term")
    d4o = build_base(root5, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED, terminal_last=False)
    res = G.grade(root5, d4o)
    ok("terminal statement present mid-log but NOT the last line on O arms -> NOT A RESULT (positional)",
       res["verdict"] == "NOT A RESULT" and any(t["arm"] == "O48" for t in res["G1"]["terminal_failures"]))

    # ---- SCRIPT arm without its .ok marker -> NOT A RESULT; terminal statement NOT composed for it
    root6 = os.path.join(scratch, "root_acc")
    d4o = build_base(root6, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED, acc_ok=False)
    res = G.grade(root6, d4o)
    ok("SCRIPT arm ACC48 with no .ok marker -> NOT A RESULT",
       res["verdict"] == "NOT A RESULT" and any(t["arm"] == "ACC48" for t in res["G1"]["terminal_failures"]))
    ok("SCRIPT arm's terminal statement is INFORMATIONAL (present in detail, not composed)",
       "terminal_statement_INFORMATIONAL_not_composed" in res["G1"]["arms"]["ACC48"]["terminal_detail"])

    # ---- stale artefact (older than the datum) -> age clause fails ----
    root7 = os.path.join(scratch, "root_stale")
    d4o = build_base(root7, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED, stale=True)
    res = G.grade(root7, d4o)
    ok("O48/opt_IPOPT.txt older than the datum -> age clause fails -> NOT A RESULT",
       res["verdict"] == "NOT A RESULT" and any(t["arm"] == "O48" for t in res["G1"]["age_failures"]))

    # ---- sign-flip pathology on 192 -> density NOT A RESULT, G-D5-1 NOT A RESULT ----
    root8 = os.path.join(scratch, "root_flip")
    d4o = build_base(root8, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED, flips192=2)
    res = G.grade(root8, d4o)
    ok("2 sign flips on density 192 -> G-D5-P_192 NOT A RESULT, G-D5-1 NOT A RESULT, item NOT A RESULT",
       res["gates"]["G-D5-P_192"] == "NOT A RESULT" and res["gates"]["G-D5-1"] == "NOT A RESULT"
       and res["verdict"] == "NOT A RESULT")
    root9 = os.path.join(scratch, "root_flip1")
    d4o = build_base(root9, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED, flips192=1)
    res = G.grade(root9, d4o)
    ok("1 sign flip on 192 -> no pathology (threshold is 2); G5d_192 GATE FAIL on the flipped component; item stays PASS",
       res["gates"]["G-D5-P_192"] == "PASS" and res["gates"]["G5d_192"] == "GATE FAIL" and res["verdict"] == "PASS")

    # ---- caps crossing -> G10 GATE FAIL ----
    root10 = os.path.join(scratch, "root_cap")
    d4o = build_base(root10, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED, cm={"O48": 900.0})
    res = G.grade(root10, d4o)
    ok("O48 at 900.0 > cap 800.0 -> G10 GATE FAIL, item GATE FAIL, P4 O48 MISS",
       res["gates"]["G10_caps"] == "GATE FAIL" and res["verdict"] == "GATE FAIL"
       and res["predictions"]["P4"]["O48"]["score"] == "MISS")

    # ---- toolchain: wrong digest -> G9 GATE FAIL ----
    root11 = os.path.join(scratch, "root_dig")
    d4o = build_base(root11, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED)
    p = os.path.join(root11, "ledger.txt")
    _t = open(p).read(); open(p, "w").write(_t.replace(G.IMG_PATCHED_DIGEST, "sha256:" + "9" * 64, 1))
    res = G.grade(root11, d4o)
    ok("one row carrying a non-PATCHED digest -> G9 GATE FAIL", res["gates"]["G9_toolchain"] == "GATE FAIL")

    # ---- placement: wrong cpuset -> G12 GATE FAIL; delivered NOT_MEASURED disclosed, not failed ----
    root12 = os.path.join(scratch, "root_cs")
    d4o = build_base(root12, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED)
    p = os.path.join(root12, "ledger.txt")
    _t = open(p).read(); open(p, "w").write(_t.replace("cpuset=8,10,11,13", "cpuset=5,6,7,9", 1)
                       .replace("delivered_cores_mean=[3.9900 n=10 max_nr_throttled=0]",
                                "delivered_cores_mean=[NOT_MEASURED]", 1))
    res = G.grade(root12, d4o)
    ok("cpuset 5,6,7,9 on one row -> G12 GATE FAIL; delivered NOT_MEASURED named, not failed",
       res["gates"]["G12_placement"] == "GATE FAIL" and len(res["G12"]["delivered_not_measured"]) == 1)

    # ---- absent physics artefact (opt_IPOPT.txt) -> REFUSE ----
    root13 = os.path.join(scratch, "root_noipopt")
    d4o = build_base(root13, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED)
    os.remove(os.path.join(root13, "O192", "opt_IPOPT.txt"))
    rf, msg = refused(G.grade, root13, d4o)
    ok("O192/opt_IPOPT.txt absent (a PHYSICS artefact) -> REFUSE", rf and "absent" in msg)

    # ---- NOT_MEASURED never composes to PASS silently: named in the verdict ----
    root14 = os.path.join(scratch, "root_nm")
    d4o = build_base(root14, cd48=2.13e-2, cd192=2.11e-2, cd96=G.CD_F_96_RECORDED)
    p = os.path.join(root14, "ledger.txt")
    _t = open(p).read(); open(p, "w").write(_t.replace("memavail_post_GiB=20.00", "memavail_post_GiB=NOT_MEASURED", 1))
    res = G.grade(root14, d4o)
    ok("a NOT_MEASURED infrastructure field on O48 -> item PASS with O48:memavail_post_GiB NAMED in not_measured",
       res["verdict"] == "PASS" and res["not_measured_named"].get("O48") == ["memavail_post_GiB"])

    print("D5 GRADE SELFTEST pass=%d fail=%d under %s" % (PASS, FAIL, mode))
    return 0 if FAIL == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
