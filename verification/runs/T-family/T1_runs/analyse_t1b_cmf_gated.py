#!/usr/bin/env python3
"""T1b PRE-EXTENSION ROWS B0-B7, GRADED THROUGH THE REGISTERED RULE-5 GATE.

WHAT THIS FILE IS.  A DRIVER, not a gate.  It applies the ALREADY-FROZEN gate
function `analyse_t1b_L4.verdict_amended` -- imported, never copied and never
reimplemented -- to the PRE-EXTENSION grid triple (c, m, f) of rung T1b, which
is the triple rows B0/B2/B4/B6 of `docs/campaigns/T-family/T1b_RESULTS.md`
rest on.  It introduces NO threshold, NO band, NO reference and NO new
measurement: the band is `T1b_band.json` (committed before any case existed),
the measurement is `analyse_t1b.measure()` and `analyse_t1c.iterative_
convergence()`, and the verdict is `verdict_amended`.  Every one of those is
frozen and every one is verified byte-identical to its HEAD blob before a
single number is read.

THE DEFECT IT CLOSES.  `analyse_t1b.py` -- the frozen comparator that produced
B0-B7 -- encodes Roache branch (1) at lines 176-187 (a level not iteratively
converged, or not plateaued across 60/70/80 D, is NOT A RESULT) and COMPUTES
the triple at line 189, but line 193 reads

    verdict = "PASS" if dev <= bpct else "GATE FAIL"

and decides WITHOUT consulting `g["state"]`.  `g["state"]` is consulted only at
line 203, and only to decide whether to print `p` and the GCI.  So branch (2)
of standing rule 5 -- a triple that is DIVERGENT, STAGNANT, OSCILLATORY or
EXACT is NOT A RESULT -- is NOT ENCODED in that instrument.  That is why
`T1b_RESULTS.md` line 29 reads `B0 | 1e4 | Nu | ... | DIVERGENT | -0.219 |
PASS`, and why its section 8 (line 316) had to apply the rule BY HAND over the
instrument: "Under that rule rows B0, B2, B4 and B6 would all read NOT A
RESULT".  A verdict cell produced by an instrument that cannot express the
gate is a standing-rule-2 shape.  The verdict must come from the instrument.

WHY NO NEW INSTRUMENT WAS BUILT.  `analyse_t1b_L4.py` already encodes branch
(2), at its lines 78-79, with negative controls at 115-121 that drive
DIVERGENT / STAGNANT / OSCILLATORY / EXACT triples lying INSIDE the band to
NOT A RESULT and CONVERGING triples inside / outside the band to PASS /
GATE FAIL.  Its gate is a PURE FUNCTION of three level values, a reference and
a band -- `verdict_amended(v1, v2, v3, reference, band)` -- and it is NOT
intrinsically scoped to (m, f, x): the frozen file's OWN selftest already calls
it on the pre-extension triple, at lines 144-151, and already asserts that the
recorded T1b (c, m, f) triples at Re 1e4 and 3e5 return NOT A RESULT.  This
driver does for all four Reynolds numbers, from the fields on disk, what that
frozen selftest already does for two from recorded constants.

WHAT IS NOT DONE HERE.
  * `analyse_t1b.py` IS NOT EDITED and IS NOT RE-RUN.  Its output stands as it
    printed.  `gate_t1b.json` is NOT rewritten; it is READ, and the frozen
    verdict is printed beside every corrected one.
  * NO SOLVER RUNS.  Every field this reads was written by the runs already on
    disk (NONCONVERGENCE_STANDARD.md L0: a reading, not a run).
  * NO VALUE MOVES.  The gate can only turn a PASS or a GATE FAIL INTO NOT A
    RESULT, never the reverse (T1b_L4_AMENDMENT.md lines 131-133).  That
    one-way direction is why applying it after the fact cannot manufacture a
    favourable verdict: it can only ever make the record more conservative.

D534 (Sanaa, 2026-08-27): REPORTED is a ROW CLASS, not a verdict.  The friction
rows B1/B3/B5/B7 are REPORTED and are EXCLUDED from the verdict census; the
tally line names them and says so.

RULE 3, THE PLANTED ZERO.  This driver's NOT A RESULT verdicts rest on
`analyse_t1c.iterative_convergence` being able to SEE a difference -- a blind
reader would report CONVERGED everywhere and branch (1) would wave every level
through.  Before grading, `planted_zero_control_t1b.py` (frozen to
`T1b_L4_PLANTED_ZERO_CONTROL_PREREGISTRATION.md`) is imported and its synthetic
arms are run; this driver REFUSES (exit 2) if that control does not pass.

GCI.  Standing rule 5: never quote a GCI when the three values are not
monotone.  `analyse_t1c.gci()` returns a `GCI_pct` key ONLY in the CONVERGING
branch, and CONVERGING requires `e32/e21 > 0`, i.e. monotone by construction.
Where the key is absent this driver PRINTS `n/a` WITH THE REASON.  It never
suppresses the field and it never invents one.

WHAT THIS DRIVER CANNOT SEE.  Everything `analyse_t1b.py` cannot (its
docstring): whether either correlation is right; a mesh-converged Nu at any Re;
the Prt, wall-function and C_lam arms, which are the frozen rung's rows and are
not touched here.  It also cannot see whether `measure()` is CORRECT -- the
planted-zero control establishes that the convergence reader is neither blind
nor noisy, not that any Nu is right.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)

import analyse_t1b as T1B                                       # noqa: E402
import analyse_t1c as T1C                                       # noqa: E402
import analyse_t1b_L4 as L4                                     # noqa: E402
import planted_zero_control_t1b as PZC                          # noqa: E402

EXIT_OK, EXIT_REFUSE, EXIT_FAIL = T1B.EXIT_OK, T1B.EXIT_REFUSE, T1B.EXIT_FAIL

LEVELS_CMF = ("c", "m", "f")
CASES_CMF = [f"R_{t}_{l}" for t in T1B.RE_TAGS for l in LEVELS_CMF]

# The frozen files this driver stands on.  Each is verified byte-identical to
# its HEAD blob before anything is read; a mismatch REFUSES.
FROZEN = (
    "verification/runs/T-family/T1_runs/analyse_t1b.py",
    "verification/runs/T-family/T1_runs/analyse_t1c.py",
    "verification/runs/T-family/T1_runs/analyse_t1b_L4.py",
    "verification/runs/T-family/T1_runs/planted_zero_control_t1b.py",
)

# The frozen comparator's own recorded Nu, from gate_t1b.json, so that a
# re-measurement that does not reproduce the record is a FINDING, not a silent
# substitution.  Relative agreement must be within this or the driver refuses.
REPRO_TOL_REL = 1e-6

# THE FROZEN GATE'S OWN PROSE IS SCOPED TO (m, f, x) AND IS NOT EDITED.
# verdict_amended is a pure function of three level values; its refusal string
# hard-codes the level names "(m,f,x)" and "the x value" because it was written
# for the L4 triple.  Applied here to (c, m, f) the NUMBERS are right and the
# LABELS are the L4 triple's.  This is disclosed on every row rather than
# repaired, because repairing it would mean editing a frozen instrument.
WHY_LABEL_CAVEAT = (
    "LABEL CAVEAT: the sentence above is verdict_amended's own frozen text, "
    "written for the (m,f,x) triple and NOT edited. Read '(m,f,x)' as the "
    "triple actually passed, which is (c,m,f), and 'the x value' as the FINE "
    "level. The state, the order and the deviation are this row's."
)


def refuse(msg):
    print(msg)
    sys.exit(EXIT_REFUSE)


def verify_freeze():
    """worktree == HEAD blob, for every frozen file this driver imports."""
    rows = []
    for rel in FROZEN:
        p = os.path.join(REPO, rel)
        try:
            head = subprocess.run(["git", "-C", REPO, "rev-parse", f"HEAD:{rel}"],
                                  capture_output=True, text=True, check=True
                                  ).stdout.strip()
            work = subprocess.run(["git", "-C", REPO, "hash-object", p],
                                  capture_output=True, text=True, check=True
                                  ).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            refuse(f"REFUSE: cannot hash {rel} against its HEAD blob ({exc})")
        ok = head == work
        rows.append((rel, head[:8], work[:8], ok))
        print(f"    {'ok ' if ok else 'BAD'} {os.path.basename(rel):32s} "
              f"HEAD {head[:8]}  worktree {work[:8]}")
    if not all(r[3] for r in rows):
        refuse("REFUSE: a frozen file this driver imports is NOT byte-identical "
               "to its HEAD blob; nothing is graded from an unfrozen instrument.")
    return [dict(path=r[0], head_blob=r[1], worktree_blob=r[2]) for r in rows]


def arm_planted_zero():
    """Rule 3.  The convergence reader must be shown able to see a non-zero."""
    rc = PZC.selftest()
    if rc != PZC.EXIT_OK:
        refuse("REFUSE: the planted-zero control did not pass; a zero from "
               "analyse_t1c.iterative_convergence is not evidence, so branch "
               "(1) of rule 5 cannot be trusted and nothing is graded.")
    return rc


def fmt_grid(g):
    """State, order and GCI -- and where a GCI may not be quoted, WHY."""
    s = g["state"]
    s += f" p={g['order']:+.3f}" if "order" in g else " p=n/a"
    if "GCI_pct" in g:
        s += f" GCI={g['GCI_pct']:.3f} %"
    else:
        s += " GCI=n/a"
    return s


def gci_reason(g):
    if "GCI_pct" in g:
        return None
    if g["state"] == "OSCILLATORY":
        return ("GCI n/a: the three values are NOT MONOTONE (e32/e21 < 0), and "
                "rule 5 forbids quoting a GCI on a non-monotone triple")
    if g["state"] == "EXACT":
        return ("GCI n/a: the two finest levels are identical (e21 = 0), so no "
                "observed order exists to extrapolate from")
    return (f"GCI n/a: the triple is {g['state']}"
            + (f" at p = {g['order']:+.3f}" if "order" in g else "")
            + "; a Richardson extrapolation off a non-converging triple is not "
              "an error bound, and rule 5 forbids quoting one")


def selftest():
    """Two arms.  Neither reads a case.

    ARM 1 delegates to the FROZEN comparator's own negative controls -- the
    DIVERGENT / STAGNANT / OSCILLATORY / EXACT triples inside the band that
    must return NOT A RESULT, and the CONVERGING triples that must reach both
    PASS and GATE FAIL.  If the gate this driver applies has been weakened,
    that is where it shows.

    ARM 2 is this driver's own PLANTED-VERDICT control: it takes the RECORDED
    T1b (c, m, f) triple at Re 1e4 -- which is DIVERGENT and which the frozen
    comparator PASSED -- shows the gate returns NOT A RESULT on it, and then
    PLANTS a perturbation in the coarse level that makes the same fine value's
    triple CONVERGING, and requires the verdict to CHANGE to PASS, and a
    further plant to reach GATE FAIL.  A driver whose verdict does not move
    when the thing it reads moves is not reading anything.
    """
    print("=== ARM 1: the frozen comparator's negative controls "
          "(analyse_t1b_L4.selftest) ===")
    ok = (L4.selftest() == L4.EXIT_OK)
    print(f"ARM 1 {'PASSED' if ok else 'FAILED'}")

    print("\n=== ARM 2: this driver's planted-verdict control on the RECORDED "
          "(c, m, f) triple at Re 1e4 ===")
    Rf, Bd = 30.906752151303174, 0.8789035978385069     # T1b_band.json, 1e4
    c, m, f = 30.11918856210323, 30.830684, 31.619274287026204
    cases = [
        ("as recorded (DIVERGENT)", c, "NOT A RESULT"),
        ("coarse planted to make the triple CONVERGING, f INSIDE band",
         f - 2.4 * (f - m), "PASS"),
        ("coarse planted CONVERGING, f driven OUTSIDE band", None, "GATE FAIL"),
    ]
    arm2 = True
    for name, cplant, expect in cases:
        if expect == "GATE FAIL":
            # same converging shape, translated so the fine value is outside
            shift = 2.0 * Bd
            v = L4.verdict_amended(f - 2.4 * (f - m) + shift, m + shift,
                                   f + shift, Rf, Bd)
        else:
            v = L4.verdict_amended(cplant, m, f, Rf, Bd)
        good = v["verdict"] == expect
        arm2 &= good
        print(f"  {'ok ' if good else 'BAD'} {name:58s} -> "
              f"{fmt_grid(v['grid']):40s} dev {v['deviation_pct']:.3f} % -> "
              f"{v['verdict']}  (expected {expect})")
    print(f"ARM 2 {'PASSED' if arm2 else 'FAILED'}"
          "  -- the verdict MOVES with what is read, so a NOT A RESULT from "
          "this driver is a reading, not a constant")

    print("\n=== ARM 3: the planted-zero control on the convergence reader ===")
    arm3 = (PZC.selftest() == PZC.EXIT_OK)
    print(f"ARM 3 {'PASSED' if arm3 else 'FAILED'}")

    allok = ok and arm2 and arm3
    print("\nSELFTEST " + ("PASSED" if allok else "FAILED"))
    return EXIT_OK if allok else EXIT_FAIL


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return selftest()

    print("### FREEZE (worktree == HEAD blob) — nothing is graded from an "
          "unfrozen instrument")
    freeze = verify_freeze()

    print("\n### RULE 3 — the planted-zero control on the convergence reader")
    arm_planted_zero()

    missing = [c for c in CASES_CMF
               if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: no completion marker for " + ", ".join(sorted(missing)))

    band = json.load(open(os.path.join(HERE, "T1b_band.json")))
    ref = {f"{r['Re']:.0f}": r for r in band["rows"]}

    frozen = {}
    for r in json.load(open(os.path.join(HERE, "gate_t1b.json")))["rows"]:
        frozen[(r["quantity"], f"{r['Re']:.0f}")] = r

    # the (m, f, x) triple, READ from the already-graded L4 artifact, not
    # re-derived here; named as read in the output and in the JSON
    mfx = {}
    p_l4 = os.path.join(HERE, "gate_t1b_L4.json")
    if os.path.isfile(p_l4):
        for r in json.load(open(p_l4))["rows"]:
            mfx[(r["quantity"], f"{r['Re']:.0f}")] = r

    out = {"driver": os.path.basename(__file__),
           "gate": "analyse_t1b_L4.verdict_amended, IMPORTED unmodified "
                   "(lines 67-86; branch (2) at 78-79)",
           "scope": "the PRE-EXTENSION triple (c, m, f), rows B0-B7 of "
                    "T1b_RESULTS.md section 1",
           "band_source": "T1b_band.json (committed before any case existed)",
           "frozen_comparator": "analyse_t1b.py, NOT edited and NOT re-run; "
                                "its verdicts read from gate_t1b.json and "
                                "printed beside",
           "mfx_source": "gate_t1b_L4.json (read, not re-derived)",
           "freeze": freeze, "rows": [], "cases": {}}
    tag_n = 0

    def m_all(case):
        """Exactly analyse_t1b_L4.main's m_all, on the (c, m, f) levels."""
        d = os.path.join(HERE, case)
        ms = {s: T1B.measure(d, s) for s in T1B.STATIONS}
        conv = T1C.iterative_convergence(d)
        nus = [ms[s]["Nu"] for s in T1B.STATIONS]
        last = T1B.STATIONS[-1]
        rec = dict(case=case, stations=ms, iterative_convergence=conv,
                   Nu=ms[last]["Nu"], Nu_station_spread=max(nus) - min(nus),
                   yplus=ms[last]["yplus"], f=ms[last]["f"], Re=ms[last]["Re"],
                   alphaEff_factor=ms[last]["alphaEff_factor"])
        out["cases"][case] = rec
        return rec

    for tag, Re in sorted(T1B.RE_TAGS.items(), key=lambda kv: kv[1]):
        key = f"{Re:.0f}"
        s = ref[key]
        Rf, Bd = s["reference"], s["band"]
        bpct = 100.0 * Bd / Rf
        print(f"\n### Re = {Re:.0f}   reference {Rf:.3f} +/- {Bd:.3f} "
              f"({bpct:.3f} %)   [midpoint of two correlations]")
        lv = {l: m_all(f"R_{tag}_{l}") for l in LEVELS_CMF}
        for l in LEVELS_CMF:
            r = lv[l]
            print(f"    {l}  Nu = {r['Nu']:9.3f}  y+ = {r['yplus']:7.3f}  "
                  f"f = {r['f']:.5f}  station spread "
                  f"{r['Nu_station_spread']:.3f}"
                  f"  [{r['iterative_convergence']['state']}]")

        # REPRODUCTION CHECK: the re-measured fine Nu must be the number the
        # record carries, or the record is not reproducible and that is the
        # finding.
        fz = frozen.get(("Nu", key))
        if fz is not None:
            rel = abs(lv["f"]["Nu"] - fz["value"]) / abs(fz["value"])
            print(f"    reproduction of gate_t1b.json Nu: measured "
                  f"{lv['f']['Nu']:.9f} vs recorded {fz['value']:.9f}, "
                  f"relative {rel:.3e}")
            if rel > REPRO_TOL_REL:
                refuse(f"REFUSE: re-measured Nu at Re {Re:.0f} does not "
                       f"reproduce gate_t1b.json (relative {rel:.3e} > "
                       f"{REPRO_TOL_REL:.0e}); the corrected verdict would not "
                       "be about the same number as the recorded one.")

        g_nu = T1C.gci(*[lv[l]["Nu"] for l in LEVELS_CMF])
        g_f = T1C.gci(*[lv[l]["f"] for l in LEVELS_CMF])
        x_nu = mfx.get(("Nu", key), {}).get("grid_mfx")
        x_f = mfx.get(("f", key), {}).get("grid_mfx")
        print(f"    Nu triple (c,m,f) MEASURED HERE : {fmt_grid(g_nu)}")
        print(f"    Nu triple (m,f,x) read from gate_t1b_L4.json: "
              + (fmt_grid(x_nu) if x_nu else "not on disk"))
        print(f"    f  triple (c,m,f) MEASURED HERE : {fmt_grid(g_f)}")
        print(f"    f  triple (m,f,x) read from gate_t1b_L4.json: "
              + (fmt_grid(x_f) if x_f else "not on disk"))
        for lbl, g in (("Nu (c,m,f)", g_nu), ("f (c,m,f)", g_f)):
            why = gci_reason(g)
            if why:
                print(f"      {lbl}: {why}")

        row = dict(row=f"B{tag_n}", Re=Re, quantity="Nu", reference=Rf,
                   band=Bd, band_pct=bpct, value=lv["f"]["Nu"],
                   levels={l: lv[l]["Nu"] for l in LEVELS_CMF},
                   grid_cmf=g_nu, grid_mfx=x_nu,
                   gci_withheld_reason=gci_reason(g_nu),
                   frozen_verdict=(fz or {}).get("verdict"),
                   dittus_boelter=s["dittus_boelter"],
                   gnielinski=s["gnielinski"])

        bad = [l for l in LEVELS_CMF
               if lv[l]["iterative_convergence"]["state"] != "CONVERGED"]
        notflat = [l for l in LEVELS_CMF
                   if lv[l]["Nu_station_spread"] > T1B.PLATEAU_FRACTION * Bd]
        if bad or notflat:
            why = []
            if bad:
                why.append("levels " + ",".join(bad) +
                           " not iteratively converged")
            if notflat:
                why.append("levels " + ",".join(notflat) +
                           " have not plateaued across 60/70/80 D")
            row.update(verdict="NOT A RESULT", branch=1, why="; ".join(why))
            out["rows"].append(row)
            print(f"    ROW B{tag_n}: NOT A RESULT [branch 1] -- "
                  f"{'; '.join(why)}")
            tag_n += 1
            continue

        v = L4.verdict_amended(lv["c"]["Nu"], lv["m"]["Nu"], lv["f"]["Nu"],
                               Rf, Bd)
        row.update(verdict=v["verdict"], deviation_pct=v["deviation_pct"],
                   branch=2 if v["verdict"] == "NOT A RESULT" else 3,
                   why=v.get("why"))
        out["rows"].append(row)
        print(f"    ROW B{tag_n}: Nu_f = {v['value']:.3f}, deviation "
              f"{v['deviation_pct']:.3f} % against band {bpct:.3f} %  "
              f"(c,m,f) {fmt_grid(g_nu)}")
        print(f"             frozen comparator returned: "
              f"{(fz or {}).get('verdict', 'not on disk')}   ->   "
              f"THIS GATE RETURNS: {v['verdict']}")
        if v.get("why"):
            print(f"             {v['why']}")
            print(f"             [{WHY_LABEL_CAVEAT}]")
            row["why_label_caveat"] = WHY_LABEL_CAVEAT
        tag_n += 1

        fref = T1B.petukhov_f(Re)
        fdev = 100.0 * abs(lv["f"]["f"] - fref) / fref
        fzf = frozen.get(("f", key))
        out["rows"].append(dict(row=f"B{tag_n}", Re=Re, quantity="f",
                                value=lv["f"]["f"], reference=fref,
                                deviation_pct=fdev, grid_cmf=g_f,
                                grid_mfx=x_f,
                                gci_withheld_reason=gci_reason(g_f),
                                levels={l: lv[l]["f"] for l in LEVELS_CMF},
                                frozen_verdict=(fzf or {}).get("verdict"),
                                row_class="REPORTED", verdict="REPORTED"))
        print(f"    ROW B{tag_n}: f = {lv['f']['f']:.5f} vs Petukhov "
              f"{fref:.5f}, {fdev:.2f} %  (c,m,f) {fmt_grid(g_f)}"
              "   [REPORTED -- D534: a ROW CLASS, not a verdict; excluded "
              "from the census]")
        tag_n += 1

    with open(os.path.join(HERE, "gate_t1b_cmf_gated.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)

    nu_rows = [r for r in out["rows"] if r["quantity"] == "Nu"]
    rep_rows = [r for r in out["rows"] if r["verdict"] == "REPORTED"]
    graded = [r for r in nu_rows if r["verdict"] in ("PASS", "GATE FAIL")]
    fails = [r for r in nu_rows if r["verdict"] == "GATE FAIL"]
    nres = [r for r in nu_rows if r["verdict"] == "NOT A RESULT"]
    out["tally"] = dict(census_rows=len(nu_rows), graded=len(graded),
                        gate_fail=len(fails), not_a_result=len(nres),
                        reported_excluded=[r["row"] for r in rep_rows])
    with open(os.path.join(HERE, "gate_t1b_cmf_gated.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)

    print(f"\n{'-'*74}")
    print(f"  CENSUS ({len(nu_rows)} Nu rows): {len(graded)} graded "
          f"({len(fails)} GATE FAIL), {len(nres)} NOT A RESULT.")
    print(f"  EXCLUDED from the census under D534 (REPORTED is a ROW CLASS, "
          f"not a verdict): {', '.join(r['row'] for r in rep_rows)} "
          f"({len(rep_rows)} friction rows).")
    print("  The VALUES are unchanged from the frozen comparator's, to "
          f"{REPRO_TOL_REL:.0e} relative, re-measured here from the fields on "
          "disk.")
    print("  The DIFFERENCE IS THE GATE, NOT THE PHYSICS: rule 5 branch (2), "
          "which analyse_t1b.py line 193 does not encode.")
    return EXIT_FAIL if fails else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
