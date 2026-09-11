#!/usr/bin/env python3
"""MRF R2 ET8000 -- ROACHE TRIPLE GRADER. FROZEN BEFORE FINE LANDS.

Written and committed while fine's `rc` sidecar does NOT exist, so the gating
order, the band logic and the estimator rule cannot have been shaped by the
answer. The absence of that sidecar is asserted in the same invocation as the
commit, so the ordering is a property of the artifact, not of anyone's word.

EVERYTHING COMES THROUGH THE FROZEN INSTRUMENTS, IMPORTED AS FUNCTIONS:
  grade_mrf_np.strict_completion            -- rule 4, run FIRST on all three
  measure_states_mrf.read_total_axial       -- total_z resolved BY NAME from the
                                               header; column -1 is viscous_z and
                                               gives plausible WRONG numbers
  measure_states_mrf.power_number, .s12
`measure_states_mrf.main()` IS NEVER CALLED: it is hardcoded to R1 at :152 and
would silently grade the wrong campaign.

THE TWO-ESTIMATOR RULE (cfd-supervisor, 2026-09-11, family law):
Np is reported by BOTH estimators, side by side, and NEITHER IS EVER QUOTED
ALONE. On the two landed levels they disagreed by 26x about whether this rung
means anything -- settled window means gave signal/noise 0.649, raw endpoints
gave 16.896. The raw-endpoint figure is two instantaneous samples of an
oscillating quantity differenced, and the difference is mostly phase: coarse's
own Np(8000)=4.193491 against a window mean of 4.228316 is a gap of 3.48e-02,
TEN TIMES the 3.36e-03 difference between the two levels' settled means.
=> A TRIPLE ON RAW ENDPOINTS CAN REPORT A CLEAN ORDER OF CONVERGENCE THAT IS AN
   ARTIFACT OF WHERE THREE OSCILLATIONS HAPPENED TO BE SAMPLED. A clean Roache
   order out of this rung is a RED FLAG, not a result.

GATING ORDER (rule 5), fixed here so it cannot be re-ordered under the pressure
of a number:
  1. any level not iteratively converged or not plateaued -> NOT A RESULT
  2. triple DIVERGENT / STAGNANT / OSCILLATORY / EXACT    -> NOT A RESULT, with
     the value, BOTH triples and BOTH orders printed beside it
  3. only CONVERGING reaches PASS (inside the pre-registered band) or GATE FAIL
  4. GCI at Fs = 1.25, NEVER quoted when the three values are not monotone
  5. the gate may turn a PASS or GATE FAIL INTO NOT A RESULT, never the reverse

exit 0 PASS | 1 GATE FAIL | 2 NOT A RESULT | 3 BLOCKED
"""
import importlib.util, os, sys, math, json, shutil, tempfile, statistics as stx

CASE = "/home/ubuntu/Certonomous/cases/navier_class/MRF"
BASE = "/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R2/ET8000"
END = 8000
LEVELS = ("coarse", "medium", "fine")
FS = 1.25            # GCI safety factor for a three-grid study
SPAN, NPTS = 600, 41  # the stopping-point spread window, as used on coarse/medium


def load(nm, p):
    s = importlib.util.spec_from_file_location(nm, p)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


gr = load("gmn", f"{CASE}/grade_mrf_np.py")
msm = load("msm", f"{CASE}/measure_states_mrf.py")


def cells(level):
    """Total cells, summed from the per-processor lines decomposePar wrote.
    Derived from the run's OWN artifact rather than from a number in a document."""
    tot, path = 0, os.path.join(BASE, level, "log.decomposePar")
    for ln in open(path, errors="ignore"):
        if "Number of cells = " in ln:
            tot += int(ln.split("=")[1].strip())
    return tot


def series(level):
    mom = os.path.join(BASE, level, "postProcessing/impellerForces/0/moment.dat")
    t, mz = msm.read_total_axial(mom)                 # QUANTITY: total_z, BY NAME
    return t, [msm.power_number(q) for q in mz], mom  # -> power number Np


def plant_ok(mom, level):
    """Rule 3, on THIS level's OWN moment.dat -- never R1's, never another level's."""
    td = tempfile.mkdtemp(prefix=f"tri_{level}_")
    pl = os.path.join(td, "m.dat"); shutil.copy(mom, pl)
    L = open(pl).read().splitlines()
    for i, ln in enumerate(L):
        if not ln.startswith("#"):
            tk = ln.replace("(", " ").replace(")", " ").split()
            L[i] = f"{tk[0]}\t({tk[1]} {tk[2]} {msm.PLANT:.12g})\t(0 0 0)\t(0 0 0)"
            break
    open(pl, "w").write("\n".join(L) + "\n")
    _, pv = msm.read_total_axial(pl)
    shutil.rmtree(td, True)
    return abs(pv[0] - msm.PLANT) <= 1e-12


def estimators(t, ser):
    """Both Np estimators at endTime, plus this level's own stopping-point noise."""
    idx = max(i for i, tt in enumerate(t) if tt <= END) + 1
    fires, drift, mono, w = msm.s12(ser[:idx])
    raw = ser[idx - 1]
    wmean = sum(ser[idx - w:idx]) / w
    step = max(1, SPAN // (NPTS - 1))
    ks = list(range(max(80, idx - SPAN), idx + 1, step))
    wm, dr = [], []
    for k in ks:
        ww = min(max(k // 4, 20), 2000)
        wm.append(sum(ser[k - ww:k]) / ww)
        dr.append(msm.s12(ser[:k])[1])
    return dict(idx=idx, raw=raw, wmean=wmean, w=w, drift=drift, mono=mono,
                fires=fires, npts=len(ks),
                wm_range=max(wm) - min(wm), wm_sd=stx.pstdev(wm),
                dr_range=max(dr) - min(dr), dr_over=sum(1 for x in dr if abs(x) >= 1e-3))


def observed_order(f1, f2, f3, r21, r32):
    """Roache/Celik apparent order. r21 != r32 here (1.5723 vs 1.5897), so the
    simple log-ratio form does NOT apply and the iterative form is used."""
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 or e32 == 0:
        return None, e21, e32
    s = e32 / e21
    if s <= 0:
        return None, e21, e32          # sign change -> oscillatory, no real order
    p = abs(math.log(abs(s)) / math.log(r21))
    for _ in range(200):               # Celik's fixed-point iteration
        q = math.log((r21 ** p - math.copysign(1, s)) / (r32 ** p - math.copysign(1, s)))
        pn = abs(math.log(abs(s)) + q) / math.log(r21)
        if abs(pn - p) < 1e-12:
            p = pn; break
        p = pn
    return p, e21, e32


def classify(f1, f2, f3):
    """COARSE, MEDIUM, FINE in that order. Returns the triple's character."""
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 and e32 == 0:
        return "EXACT"
    if e21 == 0 or e32 == 0:
        return "STAGNANT"
    if e21 * e32 < 0:
        return "OSCILLATORY"
    R = e32 / e21
    if abs(R) >= 1.0:
        return "DIVERGENT"
    return "CONVERGING"


def grade_one_estimator(name, f, r21, r32):
    """Steps 2-4 of the gating order for ONE estimator. Never a verdict on its own."""
    f1, f2, f3 = f
    kind = classify(f1, f2, f3)
    p, e21, e32 = observed_order(f1, f2, f3, r21, r32)
    print(f"    {name}: coarse {f1:.8f}  medium {f2:.8f}  fine {f3:.8f}")
    print(f"      e21 {e32 if False else e21:+.6e}   e32 {e32:+.6e}   ratio e32/e21 "
          f"{(e32/e21 if e21 else float('nan')):+.6f}")
    print(f"      TRIPLE = {kind}    observed order p = "
          f"{('%.6f' % p) if p is not None else 'UNDEFINED (sign change or zero difference)'}")
    gci = None
    if kind == "CONVERGING" and p is not None:
        ext = f3 + e32 / (r32 ** p - 1)
        gci = FS * abs(e32 / f3) / (r32 ** p - 1) * 100
        print(f"      Richardson extrapolate {ext:.8f}   GCI(fine, Fs={FS}) = {gci:.4f} %")
    else:
        print(f"      GCI NOT QUOTED -- the three values are not monotone-convergent, "
              f"and a GCI off a non-monotone triple is meaningless.")
    return kind, p, gci


def main():
    print("=" * 78)
    print("MRF R2 ET8000 -- ROACHE TRIPLE. Grader frozen before fine landed.")
    print("=" * 78)

    # ---- STEP 1: rule 4 on ALL THREE, BEFORE any number is quoted ------------
    ev = {}
    for L in LEVELS:
        d = os.path.join(BASE, L)
        try:
            ev[L] = gr.strict_completion(d, END, os.path.join(d, "log.simpleFoam"), delta_t=1.0)
            print(f"  rule-4 {L:7s} PASS  (rc={ev[L]['rc']} last_time={ev[L]['last_time']} "
                  f"exec={ev[L]['exec_count']} age_guard={ev[L]['age_guard']})")
        except (gr.Refusal, SystemExit) as e:
            print(f"  rule-4 {L:7s} REFUSED -- {e}")
            print("NOT A RESULT: a level is not shown complete. No triple is computed,")
            print("and no number from any level is quoted off an incomplete run.")
            return 2

    # ---- rule 3 plant, on EACH level's OWN moment.dat ------------------------
    S = {}
    for L in LEVELS:
        t, ser, mom = series(L)
        if not plant_ok(mom, L):
            print(f"NOT A RESULT: the reader failed its plant on {L}'s own moment.dat.")
            return 2
        S[L] = estimators(t, ser)
        print(f"  [rule 3] plant PASS on {L}'s own moment.dat (total_z resolved by name)")

    # ---- refinement ratio, in CELL LAYERS, from the runs' own artifacts ------
    N = {L: cells(L) for L in LEVELS}
    r21 = (N["medium"] / N["coarse"]) ** (1.0 / 3.0)
    r32 = (N["fine"] / N["medium"]) ** (1.0 / 3.0)
    print(f"\n  cells  coarse {N['coarse']:,}  medium {N['medium']:,}  fine {N['fine']:,}")
    print(f"  REFINEMENT RATIO IN CELL LAYERS (cube root of the cell-count ratio, 3-D):")
    print(f"    r21 = {r21:.6f}   r32 = {r32:.6f}   -- UNEQUAL, so the iterative")
    print(f"    Celik order is used and the simple log-ratio form does NOT apply.")
    if min(r21, r32) < 1.3:
        print(f"  NOTE: a refinement ratio below 1.3 is below Celik's recommended minimum.")

    # ---- STEP 1 continued: plateau state per level ---------------------------
    print("\n  PER-LEVEL STATE (S12 needs BOTH limbs; the drift limb alone is not S12):")
    not_plateaued = []
    for L in LEVELS:
        s = S[L]
        print(f"    {L:7s} drift {s['drift']:+.6e}  monotone {s['mono']:.4f}  w={s['w']}  "
              f"-> {'NOT_PLATEAUED' if s['fires'] else 'PLATEAUED'}"
              f"{'  [drift limb OVER 1e-3]' if abs(s['drift']) >= 1e-3 else ''}")
        print(f"            stopping-point spread: Np window-mean range {s['wm_range']:.6e}, "
              f"drift range {s['dr_range']:.6e} = {s['dr_range']/1e-3:.1f}x the 1e-3 limb, "
              f"limb cleared at {s['npts']-s['dr_over']}/{s['npts']}")
        if s["fires"]:
            not_plateaued.append(L)
    if not_plateaued:
        print(f"\nNOT A RESULT: {not_plateaued} did not plateau (S12 fired). Gating order")
        print("step 1 takes precedence over any triple character below.")
        return 2

    # ---- STEPS 2-4: BOTH ESTIMATORS, SIDE BY SIDE, NEITHER ALONE -------------
    print("\n  THE TWO ESTIMATORS -- BOTH PRINTED, NEITHER QUOTED ALONE:")
    res = {}
    res["settled"] = grade_one_estimator(
        "SETTLED (S12 window mean)", [S[L]["wmean"] for L in LEVELS], r21, r32)
    res["raw"] = grade_one_estimator(
        "RAW endpoint at 8000     ", [S[L]["raw"] for L in LEVELS], r21, r32)

    # ---- the meaningfulness check the pre-statement registered ---------------
    noise = max(S[L]["wm_range"] for L in LEVELS)
    d21 = abs(S["medium"]["wmean"] - S["coarse"]["wmean"])
    d32 = abs(S["fine"]["wmean"] - S["medium"]["wmean"])
    print(f"\n  SIGNAL AGAINST NOISE (the question MRF_R2_TRIPLE_PRESTATEMENT_2026-09-11.md")
    print(f"  registered BEFORE fine landed, predicting the triple would be computable")
    print(f"  but meaningless):")
    print(f"    |d21| settled {d21:.6e}   |d32| settled {d32:.6e}")
    print(f"    worst within-level stopping-point range {noise:.6e}")
    print(f"    signal/noise: d21 {d21/noise:.3f}   d32 {d32/noise:.3f}")
    meaningful = (d21 > noise) and (d32 > noise)
    print(f"    => the pre-statement is {'FALSIFIED: both gaps exceed the noise' if meaningful else 'UPHELD: a gap does NOT exceed the noise'}")
    if not meaningful:
        print("    A triple whose level-to-level differences are smaller than each level's")
        print("    own variation across nearby stopping points is ARITHMETICALLY COMPUTABLE")
        print("    AND PHYSICALLY MEANINGLESS. The numbers above are printed so the claim")
        print("    can be checked -- they are NOT a grid-convergence result.")

    # ---- THE VERDICT --------------------------------------------------------
    kinds = {k: v[0] for k, v in res.items()}
    print(f"\n  TRIPLE CHARACTER: settled={kinds['settled']}  raw={kinds['raw']}")
    if kinds["settled"] != kinds["raw"]:
        print("  THE TWO ESTIMATORS DISAGREE ABOUT THE TRIPLE'S CHARACTER. That disagreement")
        print("  is itself the finding, and no single verdict may be issued from one of them.")
        print("NOT A RESULT")
        return 2
    if kinds["settled"] != "CONVERGING":
        print(f"NOT A RESULT: the triple is {kinds['settled']}, printed above with both")
        print("triples and both orders beside it, per the gating order.")
        return 2
    if not meaningful:
        print("NOT A RESULT: the triple is CONVERGING but its differences do not exceed")
        print("the noise floor. The gate may turn a PASS INTO NOT A RESULT, never the reverse.")
        return 2
    print("The triple is CONVERGING on both estimators and its differences exceed the")
    print("noise floor. The PASS/GATE FAIL call against the pre-registered band belongs")
    print("to MRF_R2_PREREGISTRATION.md and is applied by the band check, not here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
