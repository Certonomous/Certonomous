#!/usr/bin/env python3
"""Mutation driver for the T23G2 comparator guard set.

Works ONLY on scratch copies.  Never touches /home/ubuntu/Certonomous.
__pycache__ is deleted before every run (stale bytecode inverts mutation tests).
"""
import json
import os
import re
import shutil
import subprocess
import sys

S = "/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/ht-lane-mutation"
MASTER = os.path.join(S, "repo")

CMP_REL = "docs/campaigns/T-family/analyse_t23g2.py"
RT_REL = "scripts/roache_triple.py"
MD_REL = "verification/runs/T-family/T23_runs/mark_done_t23.py"
RUNS_REL = "verification/runs/T-family/T23G2_runs"

REAL_REPO = "/home/ubuntu/Certonomous"


def sh(cmd, **kw):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)


def clear_pycache(root):
    for dp, dn, _ in os.walk(root):
        for d in list(dn):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(dp, d), ignore_errors=True)
                dn.remove(d)


class Repo:
    """A worker repo: code files are real copies, the run tree is hardlinked."""

    def __init__(self, idx):
        self.root = os.path.join(S, "work%d" % idx)
        self.build()

    def build(self):
        shutil.rmtree(self.root, ignore_errors=True)
        os.makedirs(self.root)
        for rel in ("scripts", "docs", "verification/runs/T-family/T1_runs",
                    "verification/runs/T-family/T3_runs",
                    "verification/runs/T-family/T23_runs"):
            os.makedirs(os.path.join(self.root, rel), exist_ok=True)
        sh("cp -a %s/docs/campaigns %s/docs/" % (MASTER, self.root))
        for rel in (RT_REL, MD_REL,
                    "verification/runs/T-family/T1_runs/analyse_t1c.py",
                    "verification/runs/T-family/T3_runs/analyse_t3.py"):
            sh("cp -a %s %s" % (os.path.join(MASTER, rel),
                                os.path.join(self.root, rel)))
        # the run tree is HARDLINKED from the master scratch copy: cheap, and
        # every artifact mutation below unlinks before it writes.
        sh("cp -al %s %s" % (os.path.join(MASTER, RUNS_REL),
                             os.path.join(self.root, RUNS_REL)))
        # repoint the comparator at THIS worker root
        p = os.path.join(self.root, CMP_REL)
        s = open(p).read()
        n = s.count('REPO = "%s"' % MASTER)
        if n != 1:
            raise SystemExit("REPO repoint: expected 1 occurrence, got %d" % n)
        open(p, "w").write(s.replace('REPO = "%s"' % MASTER,
                                     'REPO = "%s"' % self.root))
        self.golden = {rel: open(os.path.join(self.root, rel)).read()
                       for rel in (CMP_REL, RT_REL, MD_REL)}
        self._artifacts = []

    # ---- code ----------------------------------------------------------
    def reset_code(self):
        for rel, txt in self.golden.items():
            open(os.path.join(self.root, rel), "w").write(txt)

    def patch(self, rel, old, new, count=1):
        p = os.path.join(self.root, rel)
        s = open(p).read()
        got = s.count(old)
        if got != count:
            raise AssertionError("patch %s: expected %d occurrences of %r, "
                                 "found %d" % (rel, count, old[:70], got))
        open(p, "w").write(s.replace(old, new))

    # ---- artifacts -----------------------------------------------------
    def _remember(self, rel):
        self._artifacts.append(rel)

    def abs(self, rel):
        return os.path.join(self.root, RUNS_REL, rel)

    def read_art(self, rel):
        return open(self.abs(rel), errors="replace").read()

    def write_art(self, rel, text):
        """Unlink first, ALWAYS: the tree is hardlinked to the master copy."""
        self._remember(rel)
        p = self.abs(rel)
        if os.path.exists(p):
            os.remove(p)
        open(p, "w").write(text)

    def delete_art(self, rel):
        self._remember(rel)
        p = self.abs(rel)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)

    def touch_art(self, rel, when):
        """Unlink-and-rewrite so the mtime change cannot reach the master."""
        txt = self.read_art(rel)
        self.write_art(rel, txt)
        os.utime(self.abs(rel), (when, when))

    def reset_artifacts(self):
        for rel in self._artifacts:
            src = os.path.join(MASTER, RUNS_REL, rel)
            dst = self.abs(rel)
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            elif os.path.exists(dst):
                os.remove(dst)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            sh("cp -al %s %s" % (src, dst))
        self._artifacts = []

    # ---- runners -------------------------------------------------------
    def run_comparator(self, timeout=2400):
        clear_pycache(self.root)
        d = os.path.join(self.root, "docs/campaigns/T-family")
        r = subprocess.run([sys.executable, "analyse_t23g2.py"], cwd=d,
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout + r.stderr

    def run_markdone(self, args, timeout=600):
        clear_pycache(self.root)
        p = os.path.join(self.root, MD_REL)
        r = subprocess.run([sys.executable, p] + args, capture_output=True,
                           text=True, timeout=timeout)
        return r.returncode, r.stdout + r.stderr

    def run_md_selftest(self):
        return self.run_markdone(["--selftest"])

    def run_rt_selftest(self, timeout=600):
        clear_pycache(self.root)
        p = os.path.join(self.root, RT_REL)
        r = subprocess.run([sys.executable, p, "--selftest"],
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout + r.stderr


# =====================================================================
# THE REGISTERED MUTATIONS.  Each returns (rc, out) plus a verdict rule.
# =====================================================================
ROOT_RUNS = RUNS_REL


def _endtime_dir(lv):
    return {"T23G2_L1": "6000", "T23G2_L2": "12000", "T23G2_L3": "24000"}[lv]


MUT = {}


def mutation(mid, direction, family, guard, detector="comparator"):
    def deco(fn):
        MUT[mid] = dict(id=mid, direction=direction, family=family,
                        guard=guard, detector=detector, fn=fn)
        return fn
    return deco


# ---------------- FAMILY A: rule 4 artifacts -------------------------
@mutation("A1", "S", "rule4-completion", "conjunct 1 rc (READ path, CRASH branch)")
def a1(R):
    rel = "T23G2_L1/STATUS.T23G2_L1"
    txt = R.read_art(rel)
    txt = re.sub(r"^rc=.*$", "rc=1", txt, flags=re.M)
    if "rc=1" not in txt:
        txt += "\nrc=1\n"
    R.write_art(rel, txt)
    return R.run_comparator()


@mutation("A2", "S", "rule4-completion", "conjunct 2, the End line")
def a2(R):
    rel = "T23G2_L2/log.solve"
    txt = R.read_art(rel)
    new = re.sub(r"^End\s*$\n?", "", txt, flags=re.M)
    assert new != txt, "no End line to remove"
    R.write_art(rel, new)
    return R.run_comparator()


@mutation("A3", "S", "rule4-completion", "conjunct 3, last time == endTime")
def a3(R):
    R.delete_art("T23G2_L3/24000")
    return R.run_comparator()


@mutation("A4", "S", "rule4-completion", "conjunct 4, per-region field tuple")
def a4(R):
    R.delete_art("T23G2_L3/24000/housing/p")
    return R.run_comparator()


@mutation("A5", "S", "rule4-completion", "conjunct 6, THE AGE GUARD")
def a5(R):
    et = R.abs("T23G2_L1/6000/fluid/T")
    newest = os.path.getmtime(et)
    R.touch_art("T23G2_L1/0/housing/T", newest + 3600)
    return R.run_comparator()


@mutation("A6", "S", "rule4-completion", "CASES allow-list",
          detector="markdone-direct")
def a6(R):
    return R.run_markdone(["--root", os.path.join(R.root, ROOT_RUNS),
                           "T23G2_L4"])


@mutation("A7", "S", "rule4-completion", "read_status absent-STATUS refusal")
def a7(R):
    R.delete_art("T23G2_L1/STATUS.T23G2_L1")
    return R.run_comparator()


@mutation("A8", "S", "rule4-completion", "conjunct 5, ExecutionTime count")
def a8(R):
    rel = "T23G2_L1/log.solve"
    txt = R.read_art(rel)
    R.write_art(rel, txt + "ExecutionTime = 1 s  ClockTime = 1 s\n")
    return R.run_comparator()


# ---------------- FAMILY B: mark_done code ---------------------------
@mutation("B1", "P", "rule4-completion", "age guard", detector="md-selftest")
def b1(R):
    R.patch(MD_REL, "if os.path.getmtime(os.path.join(tdir, region, f)) < age:",
            "if os.path.getmtime(os.path.join(tdir, region, f)) < 0:")
    return R.run_md_selftest()


@mutation("B2", "P", "rule4-completion", "launcher_rc never accepted as rc",
          detector="md-selftest")
def b2(R):
    R.patch(MD_REL, 'if re.fullmatch(r"-?\\d+", st.get("rc", "")):',
            'if re.fullmatch(r"-?\\d+", st.get("rc", st.get("launcher_rc", ""))):')
    R.patch(MD_REL, 'rc = int(st["rc"])',
            'rc = int(st.get("rc", st.get("launcher_rc")))')
    return R.run_md_selftest()


@mutation("B3", "P", "rule4-completion", "conjunct 2 End count",
          detector="md-selftest")
def b3(R):
    R.patch(MD_REL,
            '    if n_end != 1:\n        fails.append("log.solve carries %d End lines',
            '    if n_end < 0:\n        fails.append("log.solve carries %d End lines')
    return R.run_md_selftest()


@mutation("B4", "P", "rule4-completion", "conjunct 4 field tuple",
          detector="md-selftest")
def b4(R):
    R.patch(MD_REL,
            'NEEDED = {\n    "fluid":   ("T", "U", "p", "p_rgh", "alphat", "nut", "k", "omega"),\n'
            '    "housing": ("T", "p"),\n    "core":    ("T", "p"),\n}',
            'NEEDED = {\n    "fluid":   ("T",),\n    "housing": (),\n    "core":    (),\n}')
    return R.run_md_selftest()


@mutation("B5", "P", "rule4-completion", "conjunct 3 endTime tolerance",
          detector="md-selftest")
def b5(R):
    R.patch(MD_REL, "if abs(last - et) > 1e-9:\n        fails.append",
            "if abs(last - et) > 1e9:\n        fails.append")
    return R.run_md_selftest()


@mutation("B6", "P", "rule4-completion", "run() honours fails",
          detector="md-selftest")
def b6(R):
    R.patch(MD_REL, "        if fails:\n            rc = EXIT_NOTDONE",
            "        if False:\n            rc = EXIT_NOTDONE")
    return R.run_md_selftest()


@mutation("B7", "P", "rule4-completion", "absent STATUS refusal (K0d L1)",
          detector="md-selftest")
def b7(R):
    R.patch(MD_REL,
            '        refuse("no STATUS.%s -- the run\'s own record was never written. An "',
            '        return {}\n        refuse("no STATUS.%s -- the run\'s own record was never written. An "')
    return R.run_md_selftest()


# ---------------- FAMILY C: roache_triple code -----------------------
@mutation("C1", "P", "rule5-gating", "NOT_A_RESULT_STATES", detector="rt-selftest")
def c1(R):
    R.patch(RT_REL,
            'NOT_A_RESULT_STATES = ("DIVERGENT", "STAGNANT", "OSCILLATORY", "EXACT",\n'
            '                       "DEGENERATE", "NO_ORDER")',
            'NOT_A_RESULT_STATES = ()')
    return R.run_rt_selftest()


@mutation("C2", "P", "rule5-gating", "_seal one-way gate", detector="rt-selftest")
def c2(R):
    R.patch(RT_REL,
            '    if finest["state"] in NOT_A_RESULT_STATES:\n        row["verdict"] = "NOT A RESULT"',
            '    if finest["state"] in NOT_A_RESULT_STATES:\n        row["verdict"] = bv')
    return R.run_rt_selftest()


@mutation("C3", "P", "rule5-gating", "_seal no-GCI-on-non-monotone",
          detector="rt-selftest")
def c3(R):
    R.patch(RT_REL,
            '    if e32 / e21 < 0.0:\n        return dict(common, state="OSCILLATORY", ratio=e32 / e21)',
            '    if e32 / e21 < 0.0:\n        _d = r ** 2.0 - 1.0\n'
            '        return dict(common, state="OSCILLATORY", ratio=e32 / e21,\n'
            '                    GCI_pct=100.0 * fs * abs(e21 / f_fine) / _d,\n'
            '                    GCI_abs=fs * abs(e21) / _d)')
    return R.run_rt_selftest()


@mutation("C4", "P", "rule5-gating", "band_verdict no-band refusal",
          detector="rt-selftest")
def c4(R):
    R.patch(RT_REL,
            '    if band is None:\n        refuse("no pre-registered band was supplied; this instrument grades "\n'
            '               "against a band fixed before compute, and will not invent one")',
            '    if band is None:\n        return "PASS", (float("-inf"), float("inf"))')
    return R.run_rt_selftest()


@mutation("C5", "P", "planted-zero", "assert_plant_control", detector="rt-selftest")
def c5(R):
    R.patch(RT_REL, '    if not pc.get("passed"):\n        refuse("planted-zero control FAILED',
            '    if False:\n        refuse("planted-zero control FAILED')
    return R.run_rt_selftest()


@mutation("C6", "P", "rule5-gating", "STAGNANT_FLOOR", detector="rt-selftest")
def c6(R):
    R.patch(RT_REL, "STAGNANT_FLOOR = 0.5", "STAGNANT_FLOOR = 0.0")
    return R.run_rt_selftest()


@mutation("C7", "P", "rule5-gating", "P_MIN / DEGENERATE", detector="rt-selftest")
def c7(R):
    R.patch(RT_REL, "P_MIN = 0.05", "P_MIN = 0.0")
    return R.run_rt_selftest()


@mutation("C8", "S", "rule5-gating", "FS = 1.25", detector="rt-selftest")
def c8(R):
    R.patch(RT_REL, "FS = 1.25 ", "FS = 3.00 ")
    return R.run_rt_selftest()


@mutation("C9", "P", "rule5-gating", "_seal one-way gate DISABLED + C2",
          detector="rt-selftest")
def c9(R):
    c2(R)
    R.patch(RT_REL, '    if row["verdict"] not in (bv, "NOT A RESULT"):',
            '    if False:')
    return R.run_rt_selftest()


# ---------------- FAMILY D: planted-zero controls --------------------
@mutation("D1", "P", "planted-zero", "control_yplus_field_reader a==b")
def d1(R):
    R.patch(CMP_REL, '_need(u_path or os.path.join(cd, et, "fluid", "U")',
            '_need(os.path.join(cd, et, "fluid", "U")')
    return R.run_comparator()


@mutation("D2", "P", "planted-zero", "control_yplus_log_reader assert")
def d2(R):
    R.patch(CMP_REL, '    p = path or os.path.join(cd, "log.yPlus.fluid")',
            '    p = os.path.join(cd, "log.yPlus.fluid")')
    return R.run_comparator()


@mutation("D3", "P", "planted-zero", "assert_plant_control in all_quantity_...")
def d3(R):
    R.patch(CMP_REL,
            '        after = _read_dat(tmp, want_field=("T" if qname in ("Q1", "Q3") else None))[-1][1]',
            '        after = _read_dat(p, want_field=("T" if qname in ("Q1", "Q3") else None))[-1][1]')
    return R.run_comparator()


@mutation("D4", "P", "planted-zero", "g_ratio's own assert (2nd line of defence)")
def d4(R):
    d3(R)
    R.patch(CMP_REL, "            RT.assert_plant_control(pc)\n            out[(qn, lv)] = pc",
            "            out[(qn, lv)] = pc")
    return R.run_comparator()


@mutation("D5", "P", "planted-zero", "g_ratio exact-zero, NO control")
def d5(R):
    R.patch(CMP_REL, "control=controls[(qn, LEVELS[-1])])", "control=None)")
    return R.run_comparator()


@mutation("D6", "P", "planted-zero", "'saw SOMETHING but not the planted quantity'")
def d6(R):
    R.patch(CMP_REL, "        nvec = _plant_u_file(up, tmp, YPLUS_PLANT_SCALE)",
            "        nvec = _plant_u_file(up, tmp, 1.0 + 2.0 * PLANT)")
    return R.run_comparator()


@mutation("D7", "P", "planted-zero", "vacuous plant -> a==b refusal")
def d7(R):
    R.patch(CMP_REL, "    if n[0] == 0:\n        refuse(", "    if False:\n        refuse(")
    R.patch(CMP_REL, "        nvec = _plant_u_file(up, tmp, YPLUS_PLANT_SCALE)",
            "        nvec = _plant_u_file(up, tmp, 1.0)")
    return R.run_comparator()


@mutation("D8", "P", "planted-zero", "YPLUS_PLANT_TOL_REL load-bearing?")
def d8(R):
    d6(R)
    R.patch(CMP_REL, "YPLUS_PLANT_TOL_REL = 1.0e-9", "YPLUS_PLANT_TOL_REL = 1.0")
    return R.run_comparator()


@mutation("D9", "P", "planted-zero", "yplus_from_log perfect-zero refusal")
def d9(R):
    rel = "T23G2_L3/log.yPlus.fluid"
    txt = R.read_art(rel)
    new = re.sub(r"(y\+\s*:\s*min\s*=\s*)[-\d.eE+]+(\s*,?\s*max\s*=\s*)[-\d.eE+]+"
                 r"(\s*,?\s*average\s*=\s*)[-\d.eE+]+",
                 r"\g<1>0\g<2>0\g<3>0", txt)
    assert new != txt, "y+ zeroing matched nothing"
    R.write_art(rel, new)
    return R.run_comparator()


@mutation("D10", "P", "planted-zero", "2% instrument-disagreement refusal")
def d10(R):
    d9(R)
    R.patch(CMP_REL,
            '    if all(v["max"] == 0.0 and v["min"] == 0.0 for v in out.values()):',
            '    if False:')
    return R.run_comparator()


# ---------------- FAMILY E: G-ORDER ----------------------------------
@mutation("E1", "S", "G-ORDER", "G-ORDER reachability (REPAIR R3)")
def e1(R):
    R.patch(CMP_REL, "ORDER_BAND = (0.5, 1.5)", "ORDER_BAND = (2.5, 3.5)")
    return R.run_comparator()


@mutation("E2", "P", "G-ORDER", "gate_order 'no row was graded' refusal")
def e2(R):
    R.patch(CMP_REL, '    for qn in ("Q4", "Q1", "Q2", "Q3", "Q6"):',
            '    for qn in ("Q1", "Q2", "Q3", "Q6"):')
    return R.run_comparator()


@mutation("E3", "P", "G-ORDER", "unevaluated gate is not a passed one")
def e3(R):
    R.patch(CMP_REL,
            '    if p is None or state != "CONVERGING":\n        verdict = "NOT A RESULT"',
            '    if p is None or state != "CONVERGING":\n        verdict = "PASS"')
    return R.run_comparator()


# ---------------- FAMILY F: G-BAND / R4 ------------------------------
@mutation("F1", "P", "G-BAND-R4", "BAND_TRANSFER_REGISTERED widened")
def f1(R):
    R.patch(CMP_REL, 'BAND_TRANSFER_REGISTERED = ("Q1", "Q3", "Q2")',
            'BAND_TRANSFER_REGISTERED = ("Q1", "Q3", "Q2", "Q4", "Q6")')
    return R.run_comparator()


@mutation("F2", "S", "G-BAND-R4", "BAND_TRANSFER_REGISTERED narrowed")
def f2(R):
    R.patch(CMP_REL, 'BAND_TRANSFER_REGISTERED = ("Q1", "Q3", "Q2")',
            'BAND_TRANSFER_REGISTERED = ("Q1",)')
    return R.run_comparator()


@mutation("F3", "P", "G-BAND-R4", "_apply_band_registration downgrade")
def f3(R):
    R.patch(CMP_REL, '        row["verdict"] = "NOT A RESULT"\n        row["why"] = ("no fine-value band',
            '        row["why"] = ("no fine-value band')
    return R.run_comparator()


# ---------------- FAMILY G: G-MESHSIM --------------------------------
@mutation("G1", "S", "G-MESHSIM", "registered-vs-built cell count")
def g1(R):
    R.patch(CMP_REL, '"T23G2_L2": 90720', '"T23G2_L2": 90721')
    return R.run_comparator()


@mutation("G2", "S", "G-MESHSIM", "registered-vs-built, from the MESH side")
def g2(R):
    # nCells = max(max(owner), max(neigh)) + 1.  Raise the largest owner index by
    # one so the BUILT mesh reports one cell more than the registration.
    rel = "T23G2_L2/constant/fluid/polyMesh/owner"
    txt = R.read_art(rel)
    i = txt.find("// * * *")
    j = txt.index("\n", i) + 1
    head, body = txt[:j], txt[j:]
    nums = [int(m.group()) for m in re.finditer(r"\b\d+\b", body)]
    mx = max(nums)
    # replace the FIRST occurrence of the max with max+1
    body2 = re.sub(r"\b%d\b" % mx, str(mx + 1), body, count=1)
    assert body2 != body
    R.write_art(rel, head + body2)
    return R.run_comparator()


@mutation("G3", "P", "G-MESHSIM", "MESHSIM_CELL_TOL similarity ratio")
def g3(R):
    R.patch(CMP_REL, "MESHSIM_CELL_TOL = 1e-9", "MESHSIM_CELL_TOL = 1.0")
    return R.run_comparator()


@mutation("G4", "P", "G-MESHSIM", "ratio checks as backstop for the total check")
def g4(R):
    g2(R)
    R.patch(CMP_REL, "        if tot != CELLS[lv]:", "        if False:")
    return R.run_comparator()


# ---------------- FAMILY H: G-CONV -----------------------------------
@mutation("H1", "S", "G-CONV", "Ux exclusion re-measured per level")
def h1(R):
    R.patch(CMP_REL, "UX_EXCLUSION_MAX = 1.0e-12", "UX_EXCLUSION_MAX = 1.0e-30")
    return R.run_comparator()


@mutation("H2", "S", "G-CONV", "Ux exclusion, from the ARTIFACT side")
def h2(R):
    rel = "T23G2_L1/6000/fluid/U"
    txt = R.read_art(rel)
    i = txt.find("// * * *")
    j = txt.index("\n", i) + 1
    head, body = txt[:j], txt[j:]
    m = re.search(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)", body)
    assert m, "no vector found"
    new = "(%s %s %s)" % (1.0e3, m.group(2), m.group(3))
    body2 = body[:m.start()] + new + body[m.end():]
    R.write_art(rel, head + body2)
    return R.run_comparator()


@mutation("H3", "P", "G-CONV", "RESID_TOL h = 1e-9 (Sanaa's tightened criterion)")
def h3(R):
    R.patch(CMP_REL, '"h": 1.0e-9', '"h": 1.0')
    return R.run_comparator()


# ---------------- FAMILY I: R2 grading path --------------------------
@mutation("I1", "S", "R2-grading-path", "grading-path member on disk")
def i1(R):
    os.remove(os.path.join(R.root,
                           "docs/campaigns/T-family/T23G2_PREREGISTRATION.md"))
    rc, out = R.run_comparator()
    sh("cp -a %s/docs/campaigns/T-family/T23G2_PREREGISTRATION.md %s/docs/campaigns/T-family/"
       % (MASTER, R.root))
    return rc, out


@mutation("I2", "S", "R2-grading-path", "grading-path member + require_done")
def i2(R):
    p = os.path.join(R.root, MD_REL)
    os.remove(p)
    rc, out = R.run_comparator()
    open(p, "w").write(R.golden[MD_REL])
    return rc, out


@mutation("I3", "P", "R2-grading-path", "the widened five-file GRADING_PATH")
def i3(R):
    R.patch(CMP_REL,
            '    "verification/runs/T-family/T23_runs/mark_done_t23.py",\n'
            '    "scripts/roache_triple.py",\n)',
            '    "scripts/roache_triple.py",\n)')
    return R.run_comparator()


# ---------------- FAMILY J: transcribed constants --------------------
@mutation("J1", "P", "transcribed-constant", "BAND_Q1")
def j1(R):
    R.patch(CMP_REL, "BAND_Q1 = (46.0, 56.0)", "BAND_Q1 = (-1e9, 1e9)")
    return R.run_comparator()


@mutation("J2", "P", "transcribed-constant", "RATIO_MIN")
def j2(R):
    R.patch(CMP_REL, "RATIO_MIN = 10.0", "RATIO_MIN = 0.0")
    return R.run_comparator()


@mutation("J3", "P", "transcribed-constant", "PLATEAU_MAX_SPREAD_K")
def j3(R):
    R.patch(CMP_REL, "PLATEAU_MAX_SPREAD_K = 0.005", "PLATEAU_MAX_SPREAD_K = 1e9")
    return R.run_comparator()


@mutation("J4", "P", "transcribed-constant", "YPLUS_MAX")
def j4(R):
    R.patch(CMP_REL, "YPLUS_MAX = 1.0", "YPLUS_MAX = 1e9")
    return R.run_comparator()


# =====================================================================
def classify(m, rc, out, base_rc, base_out):
    """KILLED / SURVIVED, by the criterion registered before the run."""
    det = m["detector"]
    if det in ("md-selftest", "rt-selftest"):
        failed = ("FAIL" in out) or rc != 0
        return ("KILLED" if failed else "SURVIVED"), _first_fail(out)
    if det == "markdone-direct":
        return ("KILLED" if rc != 0 else "SURVIVED"), _first_line(out, "REFUSE")
    # comparator
    if rc == 2:
        return "KILLED", _first_line(out, "REFUSED (exit 2)")
    if "NOT DONE" in out or "REFUSE:" in out:
        return "KILLED", _first_line(out, "NOT DONE") or _first_line(out, "REFUSE:")
    if _norm(out) == _norm(base_out) and rc == base_rc:
        return "SURVIVED", "output byte-identical to the control"
    return "SURVIVED-CHANGED", "completed with no refusal; output differs"


def _norm(t):
    return "\n".join(l for l in t.split("\n")
                     if "post-repair (working tree)" not in l)


def _first_fail(out):
    for line in out.split("\n"):
        if "FAIL" in line:
            return line.strip()[:220]
    return ""


def _first_line(out, needle):
    for line in out.split("\n"):
        if needle in line:
            return line.strip()[:260]
    return ""


def main():
    ids = sys.argv[2:]
    widx = int(sys.argv[1])
    R = Repo(widx)
    base = json.load(open(os.path.join(S, "baseline.json")))
    results = []
    for mid in ids:
        m = MUT[mid]
        R.reset_code()
        R.reset_artifacts()
        try:
            rc, out = m["fn"](R)
            verdict, msg = classify(m, rc, out, base["rc"], base["out"])
            err = ""
        except Exception as exc:                                # noqa: BLE001
            rc, out, verdict, msg = -1, "", "UNCONSTRUCTABLE", ""
            err = "%s: %s" % (type(exc).__name__, exc)
        row = dict(id=mid, direction=m["direction"], family=m["family"],
                   guard=m["guard"], detector=m["detector"], rc=rc,
                   verdict=verdict, msg=msg, error=err,
                   rung=_first_line(out, "RUNG VERDICT"))
        results.append(row)
        with open(os.path.join(S, "res_%d.jsonl" % widx), "a") as fh:
            fh.write(json.dumps(dict(row, out=out[-6000:])) + "\n")
        print("%-4s %s %-22s %s  %s" % (mid, m["direction"], verdict,
                                        m["guard"][:44], (msg or err)[:110]),
              flush=True)
    R.reset_code()
    R.reset_artifacts()




# ---- CONFIRMATION MUTATIONS, registered after B3/B5 survived their own -------
# selftest, to establish whether the survivors have TEETH on the path this rung
# actually takes.  T23G2's STATUS files carry an integer rc, so the rung is
# graded on READ-FROM-STATUS; the selftest drives those conjuncts only through
# DERIVED-FROM-LOG.  Detector is the FULL comparator on the real artifacts.

@mutation("B3x", "P", "rule4-completion",
          "B3 + the End line actually removed from L2")
def b3x(R):
    R.patch(MD_REL,
            '    if n_end != 1:\n        fails.append("log.solve carries %d End lines',
            '    if n_end < 0:\n        fails.append("log.solve carries %d End lines')
    rel = "T23G2_L2/log.solve"
    txt = R.read_art(rel)
    new = re.sub(r"^End\s*$\n?", "", txt, flags=re.M)
    assert new != txt
    R.write_art(rel, new)
    return R.run_comparator()


@mutation("B5x", "P", "rule4-completion",
          "B5 + L3's endTime dir renamed so last time != endTime")
def b5x(R):
    R.patch(MD_REL, "if abs(last - et) > 1e-9:\n        fails.append",
            "if abs(last - et) > 1e9:\n        fails.append")
    R._remember("T23G2_L3/24000")
    src = R.abs("T23G2_L3/24000")
    dst = R.abs("T23G2_L3/23900")
    sh("cp -a %s %s" % (src, dst))
    shutil.rmtree(src)
    R._artifacts.append("T23G2_L3/23900")
    return R.run_comparator()


# ---- G2 REBUILT.  As first written, G2 bumped the LIST-SIZE token rather than a
# cell index, so the intended defect was never constructed.  This version edits
# inside the parenthesised body, which is what read_scalar_list parses.
def _bump_owner_index(R, rel):
    txt = R.read_art(rel)
    i = txt.find("// * * *")
    j = txt.index("\n", i) + 1
    k = txt.index("(", j)
    e = txt.rindex(")")
    head, body, tail = txt[:k + 1], txt[k + 1:e], txt[e:]
    nums = [int(m.group()) for m in re.finditer(r"\b\d+\b", body)]
    mx = max(nums)
    body2 = re.sub(r"\b%d\b" % mx, str(mx + 1), body, count=1)
    assert body2 != body
    R.write_art(rel, head + body2 + tail)
    return mx


@mutation("G2b", "S", "G-MESHSIM", "registered-vs-built, MESH side (rebuilt)")
def g2b(R):
    _bump_owner_index(R, "T23G2_L2/constant/fluid/polyMesh/owner")
    return R.run_comparator()


@mutation("G4b", "P", "G-MESHSIM", "ratio checks as backstop (rebuilt mesh defect)")
def g4b(R):
    _bump_owner_index(R, "T23G2_L2/constant/fluid/polyMesh/owner")
    R.patch(CMP_REL, "        if tot != CELLS[lv]:", "        if False:")
    return R.run_comparator()


# ======================================================================
# PHASE 2 -- REACHABILITY.  On the as-run data EVERY graded row is NOT A
# RESULT at rule 5 step (a), because L2's p_rgh residual is 1.041e-08
# against a 1e-8 tolerance.  The band and order limbs therefore never
# execute, and a mutation to them cannot move a verdict.  The control
# below FAKES L2's convergence -- it is a HARNESS DEVICE and asserts
# nothing about the run -- purely so those guards become executable and
# their kill-rate can be measured rather than assumed.
# ======================================================================
def _make_reachable(R):
    """Lower L2's last p_rgh initial residual below the 1e-8 tolerance."""
    rel = "T23G2_L2/log.solve"
    txt = R.read_art(rel)
    ms = list(re.finditer(r"(Solving for p_rgh, Initial residual = )([\d.eE+-]+)", txt))
    assert ms, "no p_rgh residual found"
    m = ms[-1]
    R.write_art(rel, txt[:m.start()] + m.group(1) + "9.0e-09" + txt[m.end():])


def _shift_q1(R, delta=20.0):
    """Shift the WHOLE Q1 series (housing max T) on every level, so the fine
    value leaves the registered band while the triple and the plateau are
    untouched."""
    for lv in ("T23G2_L1", "T23G2_L2", "T23G2_L3"):
        rel = "%s/postProcessing/housing/housing_T/0/fieldMinMax.dat" % lv
        out = []
        for line in R.read_art(rel).split("\n"):
            f = line.split("\t")
            if line.startswith("#") or len(f) < 5 or f[1].strip() != "T":
                out.append(line)
                continue
            f[4] = repr(float(f[4]) + delta)
            out.append("\t".join(f))
        R.write_art(rel, "\n".join(out))


@mutation("R0", "S", "reachability", "the reachability control itself")
def r0(R):
    _make_reachable(R)
    return R.run_comparator()


@mutation("RQ1f", "S", "G-BAND-R4", "CONTROL: Q1 shifted OUT of the band")
def rq1f(R):
    _make_reachable(R)
    _shift_q1(R)
    return R.run_comparator()


@mutation("RQ1p", "P", "transcribed-constant",
          "BAND_Q1 widened over a Q1 that GENUINELY FAILS the band")
def rq1p(R):
    _make_reachable(R)
    _shift_q1(R)
    R.patch(CMP_REL, "BAND_Q1 = (46.0, 56.0)", "BAND_Q1 = (-1e9, 1e9)")
    return R.run_comparator()


@mutation("RF1", "P", "G-BAND-R4", "BAND_TRANSFER widened, band limb REACHABLE")
def rf1(R):
    _make_reachable(R)
    R.patch(CMP_REL, 'BAND_TRANSFER_REGISTERED = ("Q1", "Q3", "Q2")',
            'BAND_TRANSFER_REGISTERED = ("Q1", "Q3", "Q2", "Q4", "Q6")')
    return R.run_comparator()


@mutation("RF3", "P", "G-BAND-R4", "downgrade line deleted, band limb REACHABLE")
def rf3(R):
    _make_reachable(R)
    R.patch(CMP_REL,
            '        row["verdict"] = "NOT A RESULT"\n        row["why"] = ("no fine-value band',
            '        row["why"] = ("no fine-value band')
    return R.run_comparator()


@mutation("RE1", "S", "G-ORDER", "ORDER_BAND moved, G-ORDER REACHABLE")
def re1(R):
    _make_reachable(R)
    R.patch(CMP_REL, "ORDER_BAND = (0.5, 1.5)", "ORDER_BAND = (2.5, 3.5)")
    return R.run_comparator()


@mutation("H3b", "P", "G-CONV",
          "RESID_TOL p_rgh widened over a GENUINE G-CONV GATE FAIL")
def h3b(R):
    R.patch(CMP_REL, '"p_rgh": 1.0e-8', '"p_rgh": 1.0')
    return R.run_comparator()


# ---- The -O consequence of the bare asserts in t23g_readonly_diagnosis.py ----
def _run_O(R, timeout=2400):
    clear_pycache(R.root)
    d = os.path.join(R.root, "docs/campaigns/T-family")
    r = subprocess.run([sys.executable, "-O", "analyse_t23g2.py"], cwd=d,
                       capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


@mutation("G2O", "P", "G-MESHSIM",
          "corrupt owner list under python3 -O (bare asserts stripped)")
def g2o(R):
    rel = "T23G2_L2/constant/fluid/polyMesh/owner"
    txt = R.read_art(rel)
    i = txt.find("// * * *")
    j = txt.index("\n", i) + 1
    nums = [int(m.group()) for m in re.finditer(r"\b\d+\b", txt[j:])]
    mx = max(nums)
    body2 = re.sub(r"\b%d\b" % mx, str(mx + 1), txt[j:], count=1)
    R.write_art(rel, txt[:j] + body2)
    return _run_O(R)


@mutation("CLEANO", "S", "exit-contract",
          "CONTROL: the UNMUTATED comparator under python3 -O")
def cleano(R):
    return _run_O(R)


# ---- E1 / RE1 REBUILT: 'ORDER_BAND = (0.5, 1.5)' occurs twice (once in the
# A1.2 comment at :850), so the anchor is newline-delimited.
@mutation("E1b", "S", "G-ORDER", "G-ORDER reachability (REPAIR R3), rebuilt")
def e1b(R):
    R.patch(CMP_REL, "\nORDER_BAND = (0.5, 1.5)\n", "\nORDER_BAND = (2.5, 3.5)\n")
    return R.run_comparator()


@mutation("RE1b", "S", "G-ORDER", "ORDER_BAND moved, G-ORDER REACHABLE, rebuilt")
def re1b(R):
    _make_reachable(R)
    R.patch(CMP_REL, "\nORDER_BAND = (0.5, 1.5)\n", "\nORDER_BAND = (2.5, 3.5)\n")
    return R.run_comparator()


if __name__ == "__main__":
    main()
