#!/usr/bin/env python3
"""analyse_r1.py -- the A3 rung-1 patched-IDWarp reader.

WHAT THIS FILE IS, AND WHAT IT IS NOT.  PREREGISTRATION.md (frozen at 5d8e2f52) registers NO
external comparator script for this item.  The grading instrument it registers is (a) the FD3
TABLE printed by the UNCHANGED `fd3` branch of the run script -- the identical code path that
produced the archived shipped row, since D1/D2/D2b are log-only and D3 is a new branch -- and
(b) the per-component rule of section 4 applied to that table.  This file does not replace either.
It is a phase-2 lane READER: it extracts the printed values, checks the registered predictions
against them, and computes the ONE quantity the printed table does not contain, the R1-P10
analytic-vs-analytic L2.  It is committed before it runs and it changes no gate, threshold, band,
cap or label.

CLAUDE.md standing rule 3 is honoured where a ZERO could be reported: the R1-P5 bit-identity
check and the R1-P10 L2 both return "no difference" as their expected answer, so each is preceded
by a PLANTED perturbation that the same reader must SEE.  If a planted difference is invisible,
this script REFUSES (exit 2) rather than printing a zero.
"""
import os
import re
import sys
import json
import numpy as np

ROOT = "/home/ubuntu/certonomous-runs/P4-a3-rung1-patched"
ARCH = "/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/fd3_run.log"

PLANT_REL = 1.234e-03   # the planted relative perturbation, by analogy with T3_runs/analyse_t3.py

COLD_SIG = "0.5969274433533561"
ADJ_REF = [("0", "2.120880199369e-02"), ("100", "8.391224496030e-03"),
           ("200", "7.448585645712e-04"), ("300", "3.863378322670e-05"),
           ("368", "2.045016030763e-06")]
COMPS = [("patchV", 1), ("twist", 1), ("shape", 5), ("shape", 115)]
FLAGGED = {("twist", 1), ("shape", 5)}     # named in section 4 BEFORE the run


def refuse(msg):
    print("REFUSAL: %s" % msg)
    print("The reader will not report a number it cannot show itself able to read.")
    sys.exit(2)


def read(p):
    if not os.path.exists(p):
        return None
    return open(p, errors="replace").read()


# ---------------------------------------------------------------- extraction
def prov(text):
    out = {}
    for m in re.finditer(r"PROV rank (\d+) IDWARP_SO_MD5 = (\S+)", text):
        out[int(m.group(1))] = m.group(2)
    return out


def prov_paths(text):
    return {int(m.group(1)): m.group(2)
            for m in re.finditer(r"PROV rank (\d+) IDWARP_IMPORTED_FROM: (\S+)", text)}


def scalar(text, pat):
    m = re.search(pat, text)
    return m.group(1) if m else None


def adjoint_path(text):
    return [(m.group(1), m.group(2)) for m in re.finditer(
        r"^Main iteration (\d+) KSP Residual norm (\S+)", text, re.M)]


def analytic(text):
    out = {}
    for m in re.finditer(r"FD3 adjoint (\w+)\[(\d+)\] = (\S+)", text):
        out[(m.group(1), int(m.group(2)))] = m.group(3)
    return out


def perturbed_cd(text):
    return [m.group(1) for m in re.finditer(r"FD3 CD\([+-]1h\) = (\S+)", text)]


def fd_estimates(text):
    return [(m.group(1), int(m.group(2)), m.group(3), m.group(4)) for m in re.finditer(
        r"FD3 central FD (\w+)\[(\d+)\] h=(\S+): (\S+)", text)]


def table(text):
    out = {}
    for m in re.finditer(
            r"FD3 (\w+)\[(\d+)\]: adjoint (\S+)\s+FD\(h\) (\S+)\s+FD\(2h\) (\S+)\s+"
            r"stepcons (\S+)%\s+relerr (\S+)%", text):
        out[(m.group(1), int(m.group(2)))] = dict(
            adjoint=m.group(3), fdh=m.group(4), fd2h=m.group(5),
            stepcons=float(m.group(6)), relerr=float(m.group(7)))
    return out


def totals_dump(text):
    m = re.search(r"FD3 TOTALS_DUMP_BEGIN\n(.*?)\nFD3 TOTALS_DUMP_END", text, re.S)
    if not m:
        return None
    try:
        d = eval(m.group(1), {"array": np.array, "nan": np.nan, "inf": np.inf,
                              "float32": np.float32, "float64": np.float64})
    except Exception as e:                              # noqa: BLE001
        return ("PARSE_FAILURE", str(e))
    for k, v in d.items():
        wrt = k[1] if isinstance(k, tuple) else str(k)
        if wrt.endswith("shape"):
            return np.asarray(v).ravel()
    return None


def l2_rel(a, b):
    """||a - b||_2 / ||b||_2, as a percentage."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return 100.0 * float(np.linalg.norm(a - b) / np.linalg.norm(b))


# ---------------------------------------------------------------- the report
def main():
    R = {}
    logs = {a: read(os.path.join(ROOT, "%s.log" % a))
            for a in ("patched", "shipped", "wrongstep")}
    arch = read(ARCH)
    if arch is None:
        refuse("the archived shipped rung-1 log %s is missing" % ARCH)

    print("=" * 78)
    print("A3 rung 1 (21,840 cells) patched-IDWarp np=4 -- reader output")
    print("Grading instrument: the in-script FD3 TABLE (unchanged code path) + section 4.")
    print("=" * 78)

    # ---- R1-P1 provenance, per arm -------------------------------------
    print("\n[R1-P1] provenance and activity, per arm")
    want = {"patched": "85f59e87253e0a71a813f64ca6e4c425",
            "shipped": "f0fcb488e0e98156575cd19548e91663",
            "wrongstep": "85f59e87253e0a71a813f64ca6e4c425"}
    for a, t in logs.items():
        if t is None:
            print("  %-9s NO LOG -- arm did not run" % a)
            continue
        md5s = prov(t)
        ok_md5 = len(md5s) == 4 and set(md5s.values()) == {want[a]}
        tpc = "transonicPCOption 1;" in t
        sublu = t.count("DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU")
        # limb (d): the SOLVER's header, the nProcs line AFTER the DAOption dump
        idx = t.find("transonicPCOption")
        nproc4 = bool(re.search(r"^nProcs\s*:\s*4", t[idx:] if idx > 0 else t, re.M))
        npdirs = len([d for d in os.listdir(os.path.join(ROOT, a))
                      if d.startswith("processor")]) if os.path.isdir(os.path.join(ROOT, a)) else 0
        ver = set(re.findall(r"PROV rank \d+ idwarp version = (\S+)", t))
        print("  %-9s (a) 4/4 ranks md5=%s: %s | (b) transonicPCOption 1: %s | "
              "(c) sub-LU banners: %d | (d) solver nProcs:4 %s, processor* dirs %d | (e) version %s"
              % (a, want[a][:8] + "...", "YES" if ok_md5 else "NO -> %r" % md5s,
                 "YES" if tpc else "NO", sublu, "YES" if nproc4 else "NO", npdirs,
                 ",".join(sorted(ver)) or "-"))
        print("            import path rank0: %s" % prov_paths(t).get(0, "-"))
        R.setdefault("P1", {})[a] = ok_md5 and tpc and sublu == 0 and nproc4 and npdirs == 4

    # ---- R1-P2 cold start ----------------------------------------------
    print("\n[R1-P2] cold start, exact to 16 digits (registered %s)" % COLD_SIG)
    for a, t in logs.items():
        if t is None:
            continue
        got = scalar(t, r"Time step continuity errors : sum local = (\S+)")
        print("  %-9s first sum local = %s  -> %s" % (a, got, "EXACT" if got == COLD_SIG else "MISMATCH"))
        R.setdefault("P2", {})[a] = (got == COLD_SIG)

    # ---- R1-P3 colouring ------------------------------------------------
    print("\n[R1-P3] the colouring is READ, not rebuilt (registered 1233 colours)")
    for a, t in logs.items():
        if t is None:
            continue
        calc = t.count("Calculating dRdW Coloring")
        rd = "Reading Coloring dRdWColoring_4" in t
        cnt = scalar(t, r"dRdWTPC: 0 of (\d+)")
        print("  %-9s 'Calculating' occurrences=%d (must be 0) | 'Reading Coloring' %s | colours=%s"
              % (a, calc, rd, cnt))
        R.setdefault("P3", {})[a] = (calc == 0 and rd and cnt == "1233")

    # ---- R1-P4 adjoint identity -----------------------------------------
    print("\n[R1-P4] adjoint bit-identity across images, 5 printed pairs + reason/count")
    for a in ("patched", "shipped"):
        t = logs[a]
        if t is None:
            continue
        got = adjoint_path(t)[:5]
        match = (got == ADJ_REF)
        term = scalar(t, r"Total iterations: (\d+)\. PetscConvergedReason: (\d+)")
        m = re.search(r"Total iterations: (\d+)\. PetscConvergedReason: (\d+)", t)
        print("  %-9s 5/5 checkpoints match archived shipped: %s | terminal: %s iterations, reason %s"
              % (a, "YES" if match else "NO -> %r" % got,
                 m.group(1) if m else "-", m.group(2) if m else "-"))
        R.setdefault("P4", {})[a] = match and bool(m) and m.group(1) == "368" and m.group(2) == "2"

    # ---- R1-P5 the FD control, with its planted control ------------------
    print("\n[R1-P5] THE CONTROL: the FD column must not move (patched vs shipped vs archived)")
    fields = {}
    for a in ("patched", "shipped"):
        t = logs[a]
        if t is None:
            continue
        fields[a] = dict(
            b1=scalar(t, r"FD3 baseline1 CD = (\S+)"),
            b2=scalar(t, r"FD3 baseline2 CD = (\S+)"),
            drift=scalar(t, r"FD3 noise floor \|baseline drift\| = (\S+)"),
            cds=perturbed_cd(t), fds=fd_estimates(t))
    fields["archived"] = dict(
        b1=scalar(arch, r"FD3 baseline1 CD = (\S+)"),
        b2=scalar(arch, r"FD3 baseline2 CD = (\S+)"),
        drift=scalar(arch, r"FD3 noise floor \|baseline drift\| = (\S+)"),
        cds=perturbed_cd(arch), fds=fd_estimates(arch))

    # PLANTED CONTROL: corrupt one digit of a copy and require the comparator to see it.
    probe = dict(fields["archived"])
    probe["cds"] = list(probe["cds"])
    if not probe["cds"]:
        refuse("no perturbed CD values parsed from the archived log -- the reader is blind")
    victim = probe["cds"][0]
    probe["cds"][0] = victim[:-1] + ("9" if victim[-1] != "9" else "8")

    def cmp_fields(x, y):
        if x is None or y is None:
            return None
        diffs = []
        for k in ("b1", "b2", "drift"):
            if x[k] != y[k]:
                diffs.append("%s: %s vs %s" % (k, x[k], y[k]))
        if x["cds"] != y["cds"]:
            n = sum(1 for p, q in zip(x["cds"], y["cds"]) if p != q)
            diffs.append("%d of %d perturbed CD values differ" % (n, max(len(x["cds"]), len(y["cds"]))))
        if x["fds"] != y["fds"]:
            n = sum(1 for p, q in zip(x["fds"], y["fds"]) if p != q)
            diffs.append("%d of %d FD estimates differ" % (n, max(len(x["fds"]), len(y["fds"]))))
        return diffs

    seen = cmp_fields(fields["archived"], probe)
    if not seen:
        refuse("the FD comparator cannot see a planted one-digit change in a perturbed CD value")
    print("  planted-difference control: a one-digit change in CD#1 is SEEN -> %s" % seen[0])
    print("  counts parsed: patched %d CDs / %d FDs; shipped %d / %d; archived %d / %d"
          % (len(fields.get("patched", {}).get("cds", [])), len(fields.get("patched", {}).get("fds", [])),
             len(fields.get("shipped", {}).get("cds", [])), len(fields.get("shipped", {}).get("fds", [])),
             len(fields["archived"]["cds"]), len(fields["archived"]["fds"])))
    for pair in (("patched", "shipped"), ("patched", "archived"), ("shipped", "archived")):
        if pair[0] not in fields or pair[1] not in fields:
            continue
        d = cmp_fields(fields[pair[0]], fields[pair[1]])
        print("  %-9s vs %-9s : %s" % (pair[0], pair[1], "BIT-IDENTICAL" if not d else "; ".join(d)))
        R.setdefault("P5", {})["%s_vs_%s" % pair] = (not d)

    # ---- R1-P6 the literal shipped image vs the archived row -------------
    print("\n[R1-P6] does the LITERAL shipped image reproduce the archived (double-dagger) row?")
    if logs["shipped"] is not None:
        an_s, an_a = analytic(logs["shipped"]), analytic(arch)
        same_an = an_s == an_a
        d = cmp_fields(fields["shipped"], fields["archived"])
        print("  analytic values identical: %s | FD/baseline/drift: %s"
              % ("YES" if same_an else "NO -> %r vs %r" % (an_s, an_a),
                 "BIT-IDENTICAL" if not d else "; ".join(d)))
        R["P6"] = same_an and not d
    else:
        print("  arm R1-B did not run -> PENDING, never absent")

    # ---- the analytic table ---------------------------------------------
    print("\n[R1-P7/P8/P8b/P9] analytic values and the FD table")
    an = {a: analytic(logs[a]) for a in ("patched", "shipped") if logs[a] is not None}
    an["archived"] = analytic(arch)
    tb = {a: table(logs[a]) for a in ("patched", "shipped") if logs[a] is not None}
    tb["archived"] = table(arch)
    print("  %-12s %-24s %-24s %10s %10s" % ("component", "shipped analytic", "patched analytic",
                                             "delta %", "direction"))
    for c in COMPS:
        s = an.get("shipped", an["archived"]).get(c)
        p = an.get("patched", {}).get(c)
        if s is None or p is None:
            continue
        sv, pv = float(s), float(p)
        dl = 100.0 * abs(pv - sv) / abs(sv)
        direction = "toward zero" if abs(pv) < abs(sv) else "away from zero"
        print("  %-12s %-24s %-24s %10.4f %10s"
              % ("%s[%d]" % c, s, p, dl, direction))
        R.setdefault("delta", {})["%s[%d]" % c] = dict(shipped=sv, patched=pv, delta_pct=dl,
                                                       direction=direction)
    print()
    print("  %-12s %-9s %-12s %-12s %-12s %-10s" % ("component", "arm", "adjoint", "FD(h)",
                                                    "stepcons %", "relerr %"))
    for c in COMPS:
        for a in ("archived", "shipped", "patched"):
            if a in tb and c in tb[a]:
                r = tb[a][c]
                flag = "  [FLAGGED -> NOT A RESULT in the FD column]" if c in FLAGGED else ""
                print("  %-12s %-9s %-12s %-12s %-12.4f %-10.4f%s"
                      % ("%s[%d]" % c, a, r["adjoint"], r["fdh"], r["stepcons"], r["relerr"], flag))
        R.setdefault("table", {})["%s[%d]" % c] = {a: tb[a][c] for a in tb if c in tb[a]}

    # ---- R1-P10 the patch effect, analytic vs analytic --------------------
    print("\n[R1-P10] patch effect on the full 120-component analytic shape row (L2 relative)")
    gp = totals_dump(logs["patched"]) if logs["patched"] else None
    gs = totals_dump(logs["shipped"]) if logs["shipped"] else None
    if isinstance(gp, tuple) or isinstance(gs, tuple):
        refuse("the totals dump did not parse: %r" % (gp if isinstance(gp, tuple) else gs,))
    if gp is None or gs is None:
        print("  one or both TOTALS dumps absent -> R1-P10 PENDING, never absent")
    else:
        # PLANTED CONTROL first: a known relative perturbation must be SEEN at the right size.
        planted = gs.copy()
        planted[0] = planted[0] * (1.0 + PLANT_REL) if planted[0] != 0 else PLANT_REL
        expect = 100.0 * abs(gs[0]) * PLANT_REL / float(np.linalg.norm(gs))
        seen_l2 = l2_rel(planted, gs)
        if seen_l2 <= 0 or abs(seen_l2 - expect) > 1e-6 * max(1.0, expect):
            refuse("the L2 reader saw %.6e%% for a planted %.6e%% perturbation" % (seen_l2, expect))
        print("  planted-difference control: planted %.4g%% relative on component 0 -> reader "
              "reports %.6e%% (expected %.6e%%). The reader can see a non-zero." % (
                  100 * PLANT_REL, seen_l2, expect))
        L2 = l2_rel(gp, gs)
        ndiff = int(np.sum(gp != gs))
        flips = int(np.sum(np.sign(gp) * np.sign(gs) < 0))
        print("  vectors: %d components each, printed at numpy default precision" % len(gs))
        print("  ||g_patched - g_shipped||2 / ||g_shipped||2 = %.6f%%" % L2)
        print("  components differing at printed precision: %d of %d" % (ndiff, len(gs)))
        print("  analytic sign flips (NO FD exists at these indices -> no verdict): %d" % flips)
        if flips:
            idx = np.where(np.sign(gp) * np.sign(gs) < 0)[0]
            print("  sign-flip indices: %s" % list(map(int, idx)))
        R["P10"] = dict(l2_pct=L2, n_diff=ndiff, n_flips=flips, n=len(gs))

    # ---- R1-P14/P15 the trivial baseline ----------------------------------
    print("\n[R1-P14/P15] arm R1-C, the deliberately wrong FD step (h=1e-8)")
    t = logs["wrongstep"]
    if t is None:
        print("  arm R1-C did not run")
    else:
        delta = scalar(t, r"FD1W raw delta \|CD\(\+h\)-CD\(-h\)\| = (\S+)")
        thr = scalar(t, r"FD1W evaluability threshold \(10x drift \S+\) = (\S+)")
        ev = scalar(t, r"FD1W EVALUABLE = (\S+)")
        ratio = scalar(t, r"delta/threshold = (\S+)")
        fd = scalar(t, r"FD1W central FD patchV\[1\] h=1e-08: (\S+)")
        b1 = scalar(t, r"FD1W baseline1 CD = (\S+)")
        b1a = fields.get("patched", {}).get("b1")
        print("  baseline CD: R1-C %s vs R1-A %s -> %s" % (
            b1, b1a, "BIT-IDENTICAL (the reuse of R1-A's analytic is licensed)"
            if b1 == b1a else "DIFFERENT -> the control is NOT A RESULT, not compared"))
        print("  |CD(+h)-CD(-h)| = %s   threshold (10 x drift) = %s   delta/threshold = %s"
              % (delta, thr, ratio))
        print("  EVALUABLE = %s" % ev)
        if fd and an.get("patched", {}).get(("patchV", 1)):
            a1 = float(an["patched"][("patchV", 1)])
            pct = 100.0 * abs(float(fd) - a1) / abs(a1)
            print("  wrong-step FD = %s vs R1-A patched analytic %.14e -> %.4f%% "
                  "(R1-P15 carries no verdict on its own)" % (fd, a1, pct))
            R["P15_pct"] = pct
        R["P14"] = dict(delta=delta, threshold=thr, ratio=ratio, evaluable=ev,
                        baseline_matches=(b1 == b1a))

    # ---- cost -------------------------------------------------------------
    print("\n[R1-P11/P12] memory, wall and cost, from ledger.txt")
    led = read(os.path.join(ROOT, "ledger.txt"))
    total_cm = 0.0
    if led:
        for line in led.strip().splitlines():
            print("  " + line)
            m = re.search(r"core_min=(\S+)", line)
            if m:
                total_cm += float(m.group(1))
    print("  SOLVER-ARM TOTAL: %.3f core-min" % total_cm)
    R["core_min_arms"] = total_cm

    json.dump(R, open(os.path.join(ROOT, "reader_output.json"), "w"), indent=1, default=str)
    print("\nreader_output.json written to %s" % ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
