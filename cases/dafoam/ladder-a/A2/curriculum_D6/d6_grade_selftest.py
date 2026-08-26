#!/usr/bin/env python3
"""Selftest for d6_grade.py.  Run under BOTH `python3` and `python3 -O`; every
refusal must STILL FIRE under -O.  Fixtures under argv[1]; nothing touches the
registered run root, D4's run root, or docker.  Guards are shown to be the one
credited by mutating the owning constant and watching the control flip."""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d6_grade as G   # noqa: E402

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
       "ranks=4 core_min={cm} cap_core_min={cap} enforced_wall_s=30000 enforced_core_min={cap} "
       "memory=20g inspect(exit,oomkilled)=[{ke} {oom}] memavail_pre_GiB={mpre} memavail_post_GiB={mpost} "
       "cpuset={cs} delivered_cores_mean=[{dl}] siblings_pre=[] siblings_post=[] log={log}\n")


def row(arm, rc=0, ke=None, oom="false", cm=1.0, cap=None, mpre="26.00", mpost="26.00",
        dl="3.9900 n=10 max_nr_throttled=0", log=None, cs=G.CPUSET_REGISTERED, dig=G.IMG_PATCHED_DIGEST, wall=60):
    return ROW.format(arm=arm, rc=rc, ke=(rc if ke is None else ke), oom=oom, cm=cm,
                      cap=(G.CAPS[arm] if cap is None else cap), mpre=mpre, mpost=mpost, dl=dl,
                      log=(log or "%s_x.log" % arm), cs=cs, dig=dig, wall=wall)


IPOPT_TMPL = ("Number of Iterations....: {n}\n\n"
              "Objective...............:   {v:.16e}    {v:.16e}\n\n{exit}\n")


def write_ipopt(path, v, n=80, exit_="EXIT: Optimal Solution Found."):
    open(path, "w").write(IPOPT_TMPL.format(n=n, v=v, exit=exit_))


def write_fd(path, flips=0, rel=1.0):
    rows = []
    for i, (dv, idx) in enumerate(G.COMPONENTS_REGISTERED):
        j = 1.0e-3 * (i + 1)
        d = j * (1.0 + rel / 100.0)
        if i < flips:
            d = -d
        rows.append({"dv": dv, "idx": idx, "status": "PLANNED", "s_lo": 1e-3, "s_hi": 3e-3, "J_adj": repr(j),
                     "fd": {"s_lo": {"ok": True, "d": repr(d * 1.001)}, "s_hi": {"ok": True, "d": repr(d)}}})
    json.dump({"components_requested": G.COMPONENTS_REGISTERED, "rows": rows}, open(path, "w"))


def build_base(root, cd_mp, cd_ref, j0=2.60e-2, jf=2.03e-2, n_major=80, flips=0, rc=None, oom=None,
               terminal_last=True, script_ok=True, stale=False, cm=None, hst_md5_ok=True):
    if os.path.isdir(root):
        shutil.rmtree(root)
    os.makedirs(root)
    d4o = os.path.join(root, "D4_O")
    os.makedirs(d4o)
    write_ipopt(os.path.join(d4o, "opt_IPOPT.txt"), G.CD_F_D4_RECORDED)
    datum = int(time.time()) - 100
    led = open(os.path.join(root, "ledger.txt"), "w")
    led.write("ITEM=D6 staged=fixture\n")
    for arm in G.ARMS_REQUIRED:
        adir = os.path.join(root, G.ARM_DIR[arm])
        os.makedirs(os.path.join(adir, "0"), exist_ok=True)
        u = os.path.join(adir, "0", "U")
        open(u, "w").write("U\n")
        os.utime(u, (datum, datum))
        open(os.path.join(adir, ".d4_age_datum"), "w").write(str(datum))
        log = "%s_fix.log" % arm
        body = "start\nD4S_IDWARP_SO_MD5: %s\nFinalising parallel run\n" % G.IDWARP_SO_MD5_PATCHED
        if not terminal_last and arm == "O_mp":
            body += "mpirun detected abort\n"
        open(os.path.join(root, log), "w").write(body)
        if not (arm in ("ACC_mp", "REF_off") and not script_ok):
            open(os.path.join(root, log + ".ok.fix"), "w").write("")
        a_rc = (rc or {}).get(arm, 0)
        a_oom = (oom or {}).get(arm, "false")
        led.write(row(arm, rc=a_rc, oom=a_oom, cm=(cm or {}).get(arm, G.PREDICTED_CORE_MIN[arm]), log=log))
    led.close()
    omp = os.path.join(root, "O_mp")
    write_ipopt(os.path.join(omp, "opt_IPOPT.txt"), jf, n=n_major)
    open(os.path.join(omp, "OptView.hst"), "w").write("h")
    open(os.path.join(omp, "d6_endpoint_dvs.json"), "w").write("{}")
    hist = {"J": [j0] + [jf] * (n_major - 1)}
    for pt in G.POINTS:
        hist["CD_" + pt] = [cd_mp[pt] * 1.3] + [cd_mp[pt]] * (n_major - 1)
        hist["CL_" + pt] = [0.4 if pt == "cl04" else (0.5 if pt == "cl05" else 0.6)] * n_major
    json.dump(hist, open(os.path.join(omp, "d6_major_history.json"), "w"))
    write_fd(os.path.join(omp, "d6_fd_endpoint.json"), flips=flips)
    ref = os.path.join(root, "REF_off")
    hst_txt = "D4 history fixture\n" if hst_md5_ok else "moved history\n"
    open(os.path.join(ref, "OptView.hst"), "w").write(hst_txt)
    json.dump({"points": {pt: {"CD": repr(cd_ref[pt]), "CL": repr(0.5)} for pt in G.POINTS},
               "consistency_CD_cl05_minus_D4_CD_f": "0.0"}, open(os.path.join(ref, "d6_ref_off.json"), "w"))
    now = time.time()
    for dp, dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            if not (f == "U" and os.path.basename(dp) == "0"):
                os.utime(p, (now, now))
    if stale:
        p = os.path.join(omp, "opt_IPOPT.txt")
        os.utime(p, (datum - 5, datum - 5))
    return d4o


CLEAN_MP = {"cl04": 1.80e-2, "cl05": G.CD_F_D4_RECORDED + 3.0e-4, "cl06": 2.60e-2}
CLEAN_REF = {"cl04": 1.82e-2, "cl05": G.CD_F_D4_RECORDED + 3.1e-4, "cl06": 2.68e-2}


def main():
    scratch = sys.argv[1]
    os.makedirs(scratch, exist_ok=True)
    mode = "python3 -O" if not __debug__ else "python3"
    print("D6 GRADE SELFTEST under %s  grader_md5=%s" % (mode, G.md5_of(G.__file__)))
    G.MD5_D4_HST = hashlib.md5(b"D4 history fixture\n").hexdigest()   # fixture's staged-input md5

    r = G.self_assert_check()
    ok("L-332 grader carries 0 assert nodes and the counter sees a planted one",
       r["assert_nodes"] == 0 and r["counter_sees_planted"] == 1)

    p = os.path.join(scratch, "led_nm.txt")
    open(p, "w").write(row("O_mp", mpre="NOT_MEASURED", dl="NOT_MEASURED"))
    rows = G.read_ledger(p)
    ok("NOT_MEASURED infrastructure fields parse to None and are DISCLOSED",
       rows[0]["memavail_pre_GiB"] is None and "delivered" in rows[0]["infra_not_measured"])
    p = os.path.join(scratch, "led_garbage.txt")
    open(p, "w").write(row("O_mp", mpost="xyz"))
    rf, msg = refused(G.read_ledger, p)
    ok("PRESENT-BUT-GARBAGE infrastructure value -> REFUSE", rf and "row_unparseable" in msg)
    p = os.path.join(scratch, "led_nophys.txt")
    open(p, "w").write(row("O_mp").replace(" wall_s=60", ""))
    rf, msg = refused(G.read_ledger, p)
    ok("absent PHYSICS field (wall_s) -> REFUSE", rf and "row_unparseable" in msg)

    root = os.path.join(scratch, "root_clean")
    d4o = build_base(root, CLEAN_MP, CLEAN_REF)
    res = G.grade(root, d4o)
    ok("CLEAN CONTROL -> item PASS; three per-point PASS; composite 21.9 % in band; price +3.0e-4 in band",
       res["verdict"] == "PASS" and res["per_point_verdicts"] == {"cl04": "PASS", "cl05": "PASS", "cl06": "PASS"}
       and res["gates"]["G-D6-2_composite"] == "PASS" and res["gates"]["G-D6-3_price"] == "PASS",
       json.dumps(res["gates"], sort_keys=True))
    ok("planted-zero control fired on the D4 reference reader",
       abs(res["G-D6-3"]["planted_control"]["seen_delta"] - G.PLANT) < 1e-12)
    ok("P1..P7 scored: P1 HIT, P2 HIT, P3 HIT, P4 HIT, P6 HIT, P7 HIT on the clean fixture",
       all(res["predictions"][k]["score"] == "HIT" for k in ("P1", "P2", "P3", "P4", "P6", "P7")),
       json.dumps({k: v["score"] for k, v in res["predictions"].items()}))
    ok("REF_off staged input OptView.hst age-exempt BY MD5 recorded in G1",
       res["G1"]["staged_inputs"]["REF_off"]["age_exempt_by_md5"] is True)

    # per-point failure -> three verdicts, item GATE FAIL
    mp = dict(CLEAN_MP)
    mp["cl06"] = 2.70e-2
    root2 = os.path.join(scratch, "root_point")
    d4o = build_base(root2, mp, CLEAN_REF)
    res = G.grade(root2, d4o)
    ok("CD_0.6(mp) > CD_0.6(REF_off) -> G-D6-1_cl06 GATE FAIL, cl04/cl05 PASS, item GATE FAIL, P6 MISS",
       res["per_point_verdicts"] == {"cl04": "PASS", "cl05": "PASS", "cl06": "GATE FAIL"}
       and res["verdict"] == "GATE FAIL" and res["predictions"]["P6"]["score"] == "MISS")

    # composite out of band -> GATE FAIL; band mutation flips it
    root3 = os.path.join(scratch, "root_comp")
    d4o = build_base(root3, CLEAN_MP, CLEAN_REF, j0=2.60e-2, jf=2.45e-2)
    res = G.grade(root3, d4o)
    ok("composite reduction 5.8 % below 15 % -> G-D6-2 GATE FAIL, item GATE FAIL",
       res["gates"]["G-D6-2_composite"] == "GATE FAIL" and res["verdict"] == "GATE FAIL")
    gc = G.g_composite(G.read_history(root3), band=(0.0, 100.0))
    ok("GUARD MUTATION: reduction band widened -> same fixture PASS (refusal came from the band)", gc["verdict"] == "PASS")

    # price negative -> NOT A RESULT; price too large -> GATE FAIL
    mp = dict(CLEAN_MP)
    mp["cl05"] = G.CD_F_D4_RECORDED - 1.0e-5
    ref = dict(CLEAN_REF)
    ref["cl05"] = mp["cl05"] + 1e-6
    root4 = os.path.join(scratch, "root_neg")
    d4o = build_base(root4, mp, ref)
    res = G.grade(root4, d4o)
    ok("negative single-point price -> G-D6-3 NOT A RESULT, item NOT A RESULT, P3 NOT A RESULT",
       res["gates"]["G-D6-3_price"] == "NOT A RESULT" and res["verdict"] == "NOT A RESULT"
       and res["predictions"]["P3"]["score"] == "NOT A RESULT")
    mp = dict(CLEAN_MP)
    mp["cl05"] = G.CD_F_D4_RECORDED + 2.0e-3
    ref = dict(CLEAN_REF)
    ref["cl05"] = mp["cl05"] + 1e-6
    root5 = os.path.join(scratch, "root_price")
    d4o = build_base(root5, mp, ref)
    res = G.grade(root5, d4o)
    ok("price +2.0e-3 > 1.0e-3 -> G-D6-3 GATE FAIL", res["gates"]["G-D6-3_price"] == "GATE FAIL")

    # blind reader / moved reference
    def blind(path, where="x"):
        return {"objective": G.CD_F_D4_RECORDED, "exit": "EXIT: Optimal Solution Found.", "n_iter": 80,
                "optimal": True, "objective_scaled": 0.0, "path": path}
    rf, msg = refused(G.planted_zero_control, os.path.join(d4o, "opt_IPOPT.txt"), os.path.join(scratch, "ctrl"), reader=blind)
    ok("a reader that cannot see the plant -> REFUSE (rule 3)", rf and "reader_blind" in msg)
    write_ipopt(os.path.join(d4o, "opt_IPOPT.txt"), G.CD_F_D4_RECORDED + 1e-6)
    rf, msg = refused(G.grade, root5, d4o)
    ok("D4's O/opt_IPOPT.txt objective differs from the recorded CD_f -> REFUSE", rf and "d4_reference_changed" in msg)

    # completion: OOM kill -> NOT A RESULT and P7 MISS
    root6 = os.path.join(scratch, "root_oom")
    d4o = build_base(root6, CLEAN_MP, CLEAN_REF, rc={"O_mp": 137}, oom={"O_mp": "true"})
    res = G.grade(root6, d4o)
    ok("O_mp kernel exit 137 OOMKilled true -> G1 NOT A RESULT, item NOT A RESULT, P7 MISS",
       res["verdict"] == "NOT A RESULT" and res["predictions"]["P7"]["score"] == "MISS")
    p = os.path.join(root6, "ledger.txt")
    _t = open(p).read()
    open(p, "w").write(_t.replace("rc=137 ", "rc=0 ", 1))
    rf, msg = refused(G.grade, root6, d4o)
    ok("harness rc=0 vs kernel exit 137 -> REFUSE", rf and "rc_disagreement" in msg)

    root7 = os.path.join(scratch, "root_term")
    d4o = build_base(root7, CLEAN_MP, CLEAN_REF, terminal_last=False)
    res = G.grade(root7, d4o)
    ok("terminal statement not the LAST line on O_mp -> NOT A RESULT (positional)",
       res["verdict"] == "NOT A RESULT" and any(t["arm"] == "O_mp" for t in res["G1"]["terminal_failures"]))

    root8 = os.path.join(scratch, "root_script")
    d4o = build_base(root8, CLEAN_MP, CLEAN_REF, script_ok=False)
    res = G.grade(root8, d4o)
    ok("SCRIPT arms without .ok markers -> NOT A RESULT; REF_off's terminal statement not composed",
       res["verdict"] == "NOT A RESULT"
       and "terminal_statement_INFORMATIONAL_not_composed" in res["G1"]["arms"]["REF_off"]["terminal_detail"])

    root9 = os.path.join(scratch, "root_stale")
    d4o = build_base(root9, CLEAN_MP, CLEAN_REF, stale=True)
    res = G.grade(root9, d4o)
    ok("O_mp/opt_IPOPT.txt older than the datum -> age clause fails -> NOT A RESULT",
       res["verdict"] == "NOT A RESULT" and any(t["arm"] == "O_mp" for t in res["G1"]["age_failures"]))

    root10 = os.path.join(scratch, "root_hst")
    d4o = build_base(root10, CLEAN_MP, CLEAN_REF, hst_md5_ok=False)
    rf, msg = refused(G.grade, root10, d4o)
    ok("REF_off/OptView.hst md5 moved from the registered D4 md5 -> REFUSE", rf and "staged_input_md5_moved" in msg)

    root11 = os.path.join(scratch, "root_flip")
    d4o = build_base(root11, CLEAN_MP, CLEAN_REF, flips=2)
    res = G.grade(root11, d4o)
    ok("2 sign flips on the J table -> G-D6-4 NOT A RESULT, item NOT A RESULT",
       res["gates"]["G-D6-4_fd"] == "NOT A RESULT" and res["verdict"] == "NOT A RESULT")

    root12 = os.path.join(scratch, "root_cap")
    d4o = build_base(root12, CLEAN_MP, CLEAN_REF, cm={"O_mp": 2100.0})
    res = G.grade(root12, d4o)
    ok("O_mp at 2100.0 > cap 2000.0 -> G10 GATE FAIL, item GATE FAIL, P5 MISS",
       res["gates"]["G10_caps"] == "GATE FAIL" and res["verdict"] == "GATE FAIL" and res["predictions"]["P5"]["score"] == "MISS")

    root13 = os.path.join(scratch, "root_cs")
    d4o = build_base(root13, CLEAN_MP, CLEAN_REF)
    p = os.path.join(root13, "ledger.txt")
    _t = open(p).read()
    open(p, "w").write(_t.replace("cpuset=2,3,4,14", "cpuset=8,10,11,13", 1)
                       .replace("delivered_cores_mean=[3.9900 n=10 max_nr_throttled=0]", "delivered_cores_mean=[NOT_MEASURED]", 1))
    res = G.grade(root13, d4o)
    ok("cpuset 8,10,11,13 on one row -> G12 GATE FAIL; delivered NOT_MEASURED named, not failed",
       res["gates"]["G12_placement"] == "GATE FAIL" and len(res["G12"]["delivered_not_measured"]) == 1)

    root14 = os.path.join(scratch, "root_nm")
    d4o = build_base(root14, CLEAN_MP, CLEAN_REF)
    p = os.path.join(root14, "ledger.txt")
    _t = open(p).read()
    open(p, "w").write(_t.replace("memavail_post_GiB=26.00", "memavail_post_GiB=NOT_MEASURED", 1))
    res = G.grade(root14, d4o)
    ok("a NOT_MEASURED infrastructure field -> item PASS with O_mp:memavail_post_GiB NAMED",
       res["verdict"] == "PASS" and res["not_measured_named"].get("O_mp") == ["memavail_post_GiB"])

    root15 = os.path.join(scratch, "root_noref")
    d4o = build_base(root15, CLEAN_MP, CLEAN_REF)
    os.remove(os.path.join(root15, "REF_off", "d6_ref_off.json"))
    rf, msg = refused(G.grade, root15, d4o)
    ok("REF_off/d6_ref_off.json absent (a PHYSICS artefact) -> REFUSE", rf and "absent" in msg)

    print("D6 GRADE SELFTEST pass=%d fail=%d under %s" % (PASS, FAIL, mode))
    return 0 if FAIL == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
