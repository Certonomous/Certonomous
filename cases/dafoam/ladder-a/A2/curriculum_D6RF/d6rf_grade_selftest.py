#!/usr/bin/env python3
"""Curriculum D6RF -- the grader's self-test.  DRIVEN, never asserted.

Every legal outcome of `d6rf_grade.py` is produced by building a synthetic run
root that MUST produce it, and every refusal clause is driven by a mutant that
MUST fire.  `L-316` applies and is stated rather than hoped: a comparator
`--selftest` proves the GRADER, never the CASE and never the LAUNCHER.  What is
proved here is exactly: the grader's readers see what they claim to see, its
refusals fire, its ladder composes in the registered order, and its two planted
controls REFUSE a blind reader.

ZERO CONTAINERS ARE CREATED.  Zero solver core-minutes are spent.  The real
preserved run roots are never written to; the only real file this test reads is
D4's `opt_IPOPT.txt`, read-only, and the planted control asserts its md5 is
unchanged afterwards.
"""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d6rf_grade as G                                            # noqa: E402

RS6 = os.path.abspath(os.path.join(HERE, os.pardir, "curriculum_D6R",
                                   "d6r_opt_runScript.py"))
RS4 = os.path.abspath(os.path.join(HERE, os.pardir, "curriculum_D4",
                                   "d4_opt_runScript.py"))

STAMP = "20260903T000000Z_1"
LEDGER_ROW = (
    "ARM={arm} ROW={row} IMG=dafoam-idwarp-rot:v1 DIGEST={digest} rc={rc} "
    "wall_s={wall} ranks=4 core_min={cm} cap_core_min={cap} "
    "enforced_wall_s={tmo} enforced_core_min={cap:.6f} memory={mem} "
    "inspect(exit,oomkilled)=[{rc} {oom}] container_wall_s={cwall} "
    "frame_allowance_s=90 memavail_pre_GiB=28.0 memavail_post_GiB=28.0 "
    "cpuset={cpuset} delivered_cores_mean=[{deliv} n=10 max_nr_throttled=1] "
    "siblings_pre=[] siblings_post=[] log={arm}_{stamp}.log stamp={stamp}")


def _phys_d6r():
    """A PHYSICAL endpoint inside every registered bound, pinned at U0."""
    return {"_units": "PHYSICAL",
            "twist": [0.1 * i - 0.3 for i in range(7)],
            "shape": [0.01 * ((i % 11) - 5) for i in range(96)],
            "patchV_cl04": [100.0, 1.10],
            "patchV_cl05": [100.0, 1.60],
            "patchV_cl06": [100.0, 2.10]}


def _phys_d4():
    return {"_units": "PHYSICAL",
            "twist": [0.1 * i - 0.3 for i in range(7)],
            "shape": [0.01 * ((i % 11) - 5) for i in range(96)],
            "patchV": [100.0, 1.1959663232192448]}


def _fd_doc(rel_err_pct=1.0, n_flip=0, plateau_pct=2.0, statuses=None):
    """An FD artefact in the frozen producer's own shape."""
    comps = [("shape", 46), ("shape", 18), ("shape", 0), ("twist", 0),
             ("patchV_cl05", 1)]
    rows = []
    for k, (dv, idx) in enumerate(comps):
        st = (statuses or {}).get((dv, idx), "PLANNED")
        if st != "PLANNED":
            rows.append({"dv": dv, "idx": idx, "status": st, "fd": {}})
            continue
        d_hi = 1.0e-3 * (k + 1)
        jadj = d_hi * (1.0 - rel_err_pct / 100.0)
        if k < n_flip:
            jadj = -abs(jadj)
        d_lo = d_hi * (1.0 + plateau_pct / 100.0)
        rows.append({"dv": dv, "idx": idx, "status": "PLANNED",
                     "s_lo": 1.0e-3, "s_hi": 3.0e-3, "J_adj": repr(jadj),
                     "C_lo": 100.0, "C_hi": 300.0,
                     "fd": {"s_lo": {"step": 1.0e-3, "d": repr(d_lo), "ok": True},
                            "s_hi": {"step": 3.0e-3, "d": repr(d_hi), "ok": True}}})
    return {"producer_md5": "93edb4a231e13a7af065368f61a468ef",
            "components_requested": [[d, i] for d, i in comps],
            "n_components_requested": 5, "J_baseline": repr(2.0e-2),
            "J_baseline_repeat": repr(2.0e-2), "eta_raw": repr(1.0e-12),
            "eta_used": repr(1.0e-12), "eta_floored": False,
            "clearance_floor": 5.0, "ratio_min": 2.0, "plateau_tol_pct": 10.0,
            "ladder": {}, "adjoint": {}, "rows": rows, "n_rows": len(rows)}


def _hist(cd05=2.1225978108239574e-02, cd04=1.9e-2, cd06=2.6e-2, J0=2.6e-2,
          Jf=2.1e-2):
    n = 5
    return {"_source": "fixture", "_n_major_rows": n,
            "J": [repr(J0 + (Jf - J0) * i / (n - 1)) for i in range(n)],
            "CD_cl04": [repr(cd04)] * n, "CD_cl05": [repr(cd05)] * n,
            "CD_cl06": [repr(cd06)] * n,
            "CL_cl04": [repr(0.4)] * n, "CL_cl05": [repr(0.5)] * n,
            "CL_cl06": [repr(0.6)] * n}


def _refoff(cd04=2.0e-2, cd05=2.2e-2, cd06=2.8e-2):
    return {"producer_md5": "93edb4a231e13a7af065368f61a468ef",
            "J": repr(2.3e-2), "trim_wall_s": 800.0,
            "points": {"cl04": {"CL_target": 0.4, "CL": repr(0.4),
                                "CD": repr(cd04), "aoa": repr(1.1),
                                "CL_residual": repr(0.0)},
                       "cl05": {"CL_target": 0.5, "CL": repr(0.5),
                                "CD": repr(cd05), "aoa": repr(1.6),
                                "CL_residual": repr(0.0)},
                       "cl06": {"CL_target": 0.6, "CL": repr(0.6),
                                "CD": repr(cd06), "aoa": repr(2.1),
                                "CL_residual": repr(0.0)}}}


def build(root, *, arms=("F_mp", "REF_off"), rc=None, oom=None, cm=None,
          cap=None, digest=None, cpuset=None, deliv=None, cwall=None,
          fd_kwargs=None, hist_kwargs=None, refoff_kwargs=None,
          phys6=None, phys4=None, chain_terminal=None, duplicate=None,
          two_started=False, stale_product=None, mem=None):
    os.makedirs(root, exist_ok=True)
    rc = rc or {}
    datum = time.time() - 600.0
    led = []
    for arm in arms:
        led.append(LEDGER_ROW.format(
            arm=arm, row="PATCHED",
            digest=(digest or {}).get(arm, G.DIGEST_PATCHED),
            rc=(rc or {}).get(arm, 0), wall=700 if arm == "F_mp" else 900,
            cm=(cm or {}).get(arm, 46.667 if arm == "F_mp" else 60.0),
            cap=(cap or {}).get(arm, G.CAPS[arm]), tmo=G.TMO[arm],
            mem=(mem or {}).get(arm, G.MEMORY),
            oom=(oom or {}).get(arm, "false"),
            cwall=(cwall or {}).get(arm, 690 if arm == "F_mp" else 890),
            cpuset=(cpuset or {}).get(arm, G.CPUSET),
            deliv=(deliv or {}).get(arm, 3.98), stamp=STAMP))
        if duplicate == arm:
            led.append(led[-1])
    with open(os.path.join(root, "ledger.txt"), "w") as fh:
        fh.write("ITEM=D6RF\n" + "\n".join(led) + "\n")

    st = ["chain=started arms=[F_mp REF_off] pid=1 stamp=%s" % STAMP]
    if two_started:
        st.append(st[0])
    for arm in arms:
        st.append("arm=%s rc=%d stamp=%s" % (arm, (rc or {}).get(arm, 0), STAMP))
    st.append(chain_terminal or "chain=COMPLETE stamp=%s" % STAMP)
    with open(os.path.join(root, "STATUS.chain"), "w") as fh:
        fh.write("\n".join(st) + "\n")

    for arm in arms:
        log = os.path.join(root, "%s_%s.log" % (arm, STAMP))
        with open(log, "w") as fh:
            fh.write("D4S_CONTAINER_UID: 0\n"
                     "D4S_IDWARP_SO_MD5: %s\n"
                     "some solver output\n"
                     "Finalising parallel run\n" % G.IDWARP_SO_MD5)
        if G.ARM_KIND[arm] == "SCRIPT":
            open(log + ".ok." + STAMP, "w").close()
        wd = os.path.join(root, G.ARM_DIR[arm])
        os.makedirs(wd, exist_ok=True)
        with open(os.path.join(wd, ".d4_age_datum"), "w") as fh:
            fh.write("%d\n" % int(datum))
        if arm == "F_mp":
            payload = {
                "d6rf_endpoint_dvs_PHYSICAL.json": phys6 or _phys_d6r(),
                "d6r_endpoint_dvs.json": phys6 or _phys_d6r(),
                "d6r_endpoint_dvs_DRIVERSCALED.json": {"twist": [0.0]},
                "d6r_major_history.json": _hist(**(hist_kwargs or {})),
                "d6r_fd_endpoint.json": _fd_doc(**(fd_kwargs or {})),
            }
        else:
            payload = {
                "d4_endpoint_dvs_PHYSICAL.json": phys4 or _phys_d4(),
                "d4_endpoint_dvs.json": phys4 or _phys_d4(),
                "d6r_ref_off.json": _refoff(**(refoff_kwargs or {})),
            }
        for name, doc in payload.items():
            p = os.path.join(wd, name)
            with open(p, "w") as fh:
                json.dump(doc, fh, indent=1, sort_keys=True)
            if stale_product == name:
                os.utime(p, (datum - 60, datum - 60))
    return root


def run():
    ok, fail = [], []
    tmp = tempfile.mkdtemp(prefix="d6rf_grade_st_")
    n = [0]

    def drive(label, want_verdict=None, want_refusal=False, **kw):
        n[0] += 1
        root = build(os.path.join(tmp, "r%02d" % n[0]), **kw)
        out = os.path.join(tmp, "r%02d.json" % n[0])
        try:
            doc = G.grade(root, out, skip_freeze=True, runscript_d6r=RS6,
                          runscript_d4=RS4)
            got = doc["verdict"]
            detail = "; ".join(doc["verdict_reasons"])[:130]
        except G.Refusal as e:
            got, detail = "REFUSED", str(e)[:130]
        except Exception as e:                                    # noqa: BLE001
            got, detail = "EXCEPTION:%s" % type(e).__name__, repr(e)[:130]
        want = "REFUSED" if want_refusal else want_verdict
        good = (got == want)
        print("  %-2d %-52s want=%-13s got=%-13s %s"
              % (n[0], label, want, got, "PASS" if good else "FAIL"))
        if detail:
            print("        %s" % detail)
        (ok if good else fail).append(label)
        return None

    def bare(label, fn, want_refusal=True):
        try:
            fn()
            got, detail = "no-refusal", ""
        except G.Refusal as e:
            got, detail = "REFUSED", str(e)[:130]
        except Exception as e:                                    # noqa: BLE001
            got, detail = "EXCEPTION:%s" % type(e).__name__, repr(e)[:130]
        want = "REFUSED" if want_refusal else "no-refusal"
        good = (got == want)
        print("  -- %-52s want=%-13s got=%-13s %s"
              % (label, want, got, "PASS" if good else "FAIL"))
        if detail:
            print("        %s" % detail)
        (ok if good else fail).append(label)

    print("D6RF GRADER SELFTEST -- every outcome DRIVEN, zero containers\n")
    print("A. THE CLEAN CONTROL AND THE LADDER")
    drive("clean two-arm root, everything inside band", "PASS")
    drive("FD rel err 9 % > the registered 5 % band", "GATE FAIL",
          fd_kwargs={"rel_err_pct": 9.0})
    drive("FD plateau 25 % > the registered 10 % tolerance", "GATE FAIL",
          fd_kwargs={"plateau_pct": 25.0})
    drive("ONE sign flip -- GATE FAIL, not the pathology", "GATE FAIL",
          fd_kwargs={"n_flip": 1})
    drive("TWO sign flips -- the registered pathology", "NOT A RESULT",
          fd_kwargs={"n_flip": 2})
    drive("a component NEAR_ZERO -- no FD pair was taken", "NOT A RESULT",
          fd_kwargs={"statuses": {("twist", 0): "NEAR_ZERO"}})
    drive("per-point CD_mp above CD_REF_off at cl06", "GATE FAIL",
          refoff_kwargs={"cd06": 2.4e-2})
    drive("single-point price above the 1.0e-3 band", "GATE FAIL",
          hist_kwargs={"cd05": 2.3e-2})
    drive("NEGATIVE single-point price -- a finding about D4", "NOT A RESULT",
          hist_kwargs={"cd05": 2.0e-2})

    print("\nB. COMPLETION, THE AGE GUARD AND THE CENSUS")
    drive("rc != 0 on an arm that ran", "NOT A RESULT", rc={"F_mp": 1})
    drive("OOMKilled true", "NOT A RESULT", oom={"F_mp": "true"})
    drive("a registered product OLDER than the arm's own age datum",
          "NOT A RESULT", stale_product="d6r_fd_endpoint.json")
    drive("REF_off never ran, chain accounts for it", "NOT A RESULT",
          arms=("F_mp",),
          chain_terminal="chain=STOPPED_AT_FIRST_NONZERO arm=F_mp rc=124 "
                         "order=[F_mp REF_off] not_run=[REF_off] stamp=%s" % STAMP)
    drive("an arm missing while the chain says COMPLETE", want_refusal=True,
          arms=("F_mp",))
    drive("a duplicate ledger row for one arm", want_refusal=True,
          duplicate="F_mp")
    drive("two chain=started lines (a second fire)", want_refusal=True,
          two_started=True)

    print("\nC. THE LOCUS CONTROLS -- the defect this item exists to repair")
    ds = {"_units": "PHYSICAL",
          "twist": [0.01 * i for i in range(7)],
          "shape": [0.1 * ((i % 11) - 5) * 10.0 for i in range(96)],
          "patchV_cl04": [10.0, 0.11], "patchV_cl05": [10.0, 0.16],
          "patchV_cl06": [10.0, 0.21]}
    drive("F_mp's PHYSICAL artefact still DRIVER-SCALED (the live defect)",
          "NOT A RESULT", phys6=ds)
    bad_bounds = _phys_d6r()
    bad_bounds["shape"][0] = 1.5
    drive("one shape component outside its registered [-1, 1] bound",
          "NOT A RESULT", phys6=bad_bounds)
    unpinned = _phys_d6r()
    unpinned["patchV_cl05"][0] = 99.9
    drive("a pinned witness moved off U0 by 0.1 %", "NOT A RESULT",
          phys6=unpinned)
    noflag = _phys_d6r()
    del noflag["_units"]
    drive("the artefact does not declare itself PHYSICAL", "NOT A RESULT",
          phys6=noflag)

    print("\nD. CAPS, TOOLCHAIN, PLACEMENT")
    drive("core_min above the registered cap", "GATE FAIL",
          cm={"F_mp": 481.0})
    drive("container clock beyond deadline + kill grace", "GATE FAIL",
          cwall={"F_mp": 7300})
    drive("host-minus-container gap above the 30 s limb", "GATE FAIL",
          cwall={"F_mp": 600})
    drive("an absent container clock -> NOT_MEASURED, host bracket stands",
          "PASS", cwall={"F_mp": "NOT_MEASURED", "REF_off": "NOT_MEASURED"})
    drive("the SHIPPED digest on a row", "GATE FAIL",
          digest={"F_mp": G.DIGEST_SHIPPED})
    drive("cpuset moved off the registered set", "GATE FAIL",
          cpuset={"REF_off": "0,1,2,3"})
    drive("delivered cores below the registered 3.0 floor", "GATE FAIL",
          deliv={"F_mp": 2.1})
    drive("delivered cores NOT_MEASURED -> disclosed, not failed", "PASS",
          deliv={"F_mp": "NOT_MEASURED"})
    drive("container memory not the registered 20g", "GATE FAIL",
          mem={"F_mp": "8g"})

    print("\nE. THE PLANTED-ZERO CONTROLS (rule 3) -- a blind reader REFUSES")
    root = build(os.path.join(tmp, "plant"))
    fd_path = os.path.join(root, "F_mp", "d6r_fd_endpoint.json")
    ctrl = os.path.join(tmp, "plant_ctrl")
    res = G.run_planted_controls(ctrl, fd_path)
    seen_fd = res["fd_control"]["reader_saw_the_plant"]
    seen_pr = res["price_control"]["reader_saw_the_plant"]
    print("  -- FD control:    delta %.6e, reader saw the plant: %s"
          % (res["fd_control"]["delta"], seen_fd))
    print("  -- price control: delta %.6e, reader saw the plant: %s"
          % (res["price_control"]["delta"], seen_pr))
    (ok if seen_fd else fail).append("plant/fd-reader-sees-a-live-plant")
    (ok if seen_pr else fail).append("plant/price-reader-sees-a-live-plant")
    unchanged = (res["fd_control"]["original_unchanged"]
                 and res["price_control"]["original_unchanged"])
    print("  -- both originals byte-unchanged by the control: %s" % unchanged)
    (ok if unchanged else fail).append("plant/originals-unchanged")

    real_fd, real_pr = G.read_fd, G.read_d4_cd_f
    try:
        G.read_fd = lambda p: real_fd(fd_path)          # BLIND: ignores its arg
        bare("a BLIND FD reader (returns the unperturbed file whatever it is "
             "given)", lambda: G.run_planted_controls(
                 os.path.join(tmp, "blind_fd"), fd_path))
    finally:
        G.read_fd = real_fd
    try:
        G.read_d4_cd_f = lambda p: real_pr(G.D4_OPT_IPOPT)          # BLIND
        bare("a BLIND price reader", lambda: G.run_planted_controls(
            os.path.join(tmp, "blind_price"), fd_path))
    finally:
        G.read_d4_cd_f = real_pr
    bare("an FD artefact with NO plantable PLANNED row",
         lambda: G.run_planted_controls(
             os.path.join(tmp, "noplant"),
             _write(os.path.join(tmp, "noplant.json"),
                    _fd_doc(statuses={c: "NEAR_ZERO" for c in
                                      [("shape", 46), ("shape", 18),
                                       ("shape", 0), ("twist", 0),
                                       ("patchV_cl05", 1)]}))))

    print("\nF. THE REFERENCE AND THE FREEZE")
    moved = os.path.join(tmp, "d4_moved.txt")
    shutil.copy2(G.D4_OPT_IPOPT, moved)
    with open(moved) as fh:
        txt = fh.read().replace("2.1125978108239574e-02", "9.9999999999999999e-02")
    with open(moved, "w") as fh:
        fh.write(txt)
    root = build(os.path.join(tmp, "ref"))
    bare("D4's recorded reference has MOVED on disk",
         lambda: G.grade(root, os.path.join(tmp, "ref.json"), skip_freeze=True,
                         runscript_d6r=RS6, runscript_d4=RS4, d4_ref=moved))
    G.D4_OPT_IPOPT = ("/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/"
                      "O/opt_IPOPT.txt")
    bare("the freeze check on an uncommitted path",
         lambda: G.freeze_check(["cases/dafoam/ladder-a/A2/curriculum_D6RF/"
                                 "NOT_A_FILE.md"]))

    print("\nD6RF_GRADE_SELFTEST %d/%d PASS" % (len(ok), len(ok) + len(fail)))
    if fail:
        print("FAILED: %s" % ", ".join(fail))
        return 1
    return 0


def _write(path, doc):
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
    return path


if __name__ == "__main__":
    sys.exit(run())
