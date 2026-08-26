#!/usr/bin/env python3
"""D7FR PRE-LAUNCH MEMORY GATE -- A WINDOW, NOT A SAMPLE.

WHY THIS FILE EXISTS.  D7FR's frozen launcher gates on ONE reading of
`MemAvailable` taken immediately before launch.  MEASURED on this box on
2026-08-26: `MemAvailable` is not low, it OSCILLATES -- median 17.35 GiB, min
1.96 GiB, and below the lab's ABSOLUTE 12 GiB floor in 19 of 45 samples.  At
that duty cycle a one-shot gate reads the comfortable mode about three times in
five and PASSES, and the run then meets an excursion it has no rule to survive:
D7R sec.8 registered the in-run sampler as record-only with NO mid-run stop,
deliberately, because killing a converging optimisation to protect a number
destroys the run it protects.

  A SINGLE-SAMPLE GATE ON A TIME-VARYING QUANTITY IS NOT A WEAK GATE.  IT IS THE
  WRONG INSTRUMENT FOR THE QUANTITY.

This is heat-transfer's Class A -> Class C shape, and that team already built the
answer (`analyse_e4a2.py:300`, `analyse_k0cx.py:644`): a sustained window, a
trend rejection, a stationarity check, and a REFUSAL below a minimum sample
count.  It is the same shape as cfd's T8 lesson -- one residual reading is not
evidence of convergence, because a converging trend is a property of a HISTORY
and not of a sample.  MEMORY HEADROOM IS A HISTORY TOO.

THE FOUR REFUSALS, and every one of them is demonstrated firing by --selftest:

  R1 COUNT       fewer than MIN_SAMPLES readings -> REFUSE.  A window that is
                 not a window cannot show an excursion (L-302).
  R2 SPAN        a window shorter than MIN_WINDOW_S -> REFUSE.  Twenty samples
                 taken in two seconds are one sample with extra steps.
  R3 EXCURSION   ANY sample below the arm's registered floor -> REFUSE.  NOT the
                 median, NOT the mean, NOT the last reading.  A median of 17.35
                 with a minimum of 1.96 MUST FAIL, and any gate that passes it
                 is measuring the wrong statistic.
  R4 TREND       a downward slope that projects below the floor within the arm's
                 registered wall-clock budget -> REFUSE, even if no sample in
                 the window has crossed it yet.

THIS GATE ONLY EVER REFUSES.  It cannot turn a refusal into a launch and it
holds no threshold of its own: the floor is the arm's REGISTERED floor, passed
in, never chosen here.

REFUSES (exit 2) rather than degrading.  No `assert` anywhere: every refusal is
a real branch, so `python3 -O` cannot strip one.
"""
import argparse
import json
import sys

MIN_SAMPLES = 20          # R1
MIN_WINDOW_S = 30.0       # R2


class Refuse(Exception):
    pass


def refuse(rid, detail):
    raise Refuse("%s: %s" % (rid, json.dumps(detail, sort_keys=True)))


def gate(samples, floor_gib, span_s, arm_wall_s=None):
    """samples: MemAvailable GiB, oldest first.  REFUSES or returns a report."""
    n = len(samples)
    if n < MIN_SAMPLES:
        refuse("R1_COUNT", {"n_samples": n, "minimum": MIN_SAMPLES,
                            "note": "a window that is not a window cannot show "
                                    "an excursion (L-302)"})
    if span_s < MIN_WINDOW_S:
        refuse("R2_SPAN", {"window_s": span_s, "minimum_s": MIN_WINDOW_S,
                           "note": "N samples taken instantaneously are one "
                                   "sample with extra steps"})
    below = [(i, v) for i, v in enumerate(samples) if v < floor_gib]
    stats = {"n_samples": n, "window_s": span_s, "floor_gib": floor_gib,
             "min": min(samples), "max": max(samples),
             "median": sorted(samples)[n // 2],
             "mean": round(sum(samples) / n, 4),
             "n_below_floor": len(below)}
    if below:
        refuse("R3_EXCURSION",
               dict(stats, first_excursion_at_index=below[0][0],
                    worst=min(v for _, v in below),
                    note="ANY sample below the floor refuses -- never the "
                         "median, never the mean, never the last reading"))
    # R4: least-squares slope in GiB per second, projected forward.
    mx = (n - 1) / 2.0
    my = sum(samples) / n
    den = sum((i - mx) ** 2 for i in range(n))
    slope_per_sample = (sum((i - mx) * (v - my) for i, v in enumerate(samples))
                        / den) if den else 0.0
    per_s = slope_per_sample * (n - 1) / span_s if span_s else 0.0
    stats["slope_gib_per_min"] = round(per_s * 60.0, 4)
    if arm_wall_s and per_s < 0:
        projected = samples[-1] + per_s * arm_wall_s
        stats["projected_at_arm_end_gib"] = round(projected, 3)
        stats["arm_wall_s"] = arm_wall_s
        if projected < floor_gib:
            refuse("R4_TREND",
                   dict(stats, note="the window has not crossed the floor but "
                                    "its own slope reaches it inside this arm's "
                                    "registered wall budget"))
    stats["verdict"] = "CLEAR"
    return stats


def _read(path):
    return [float(x) for x in open(path) if x.strip()]


def selftest():
    units = []

    def unit(name, want, got, detail=""):
        units.append({"u": name, "ok": want == got, "w": want, "g": got, "d": detail})

    def fires(label, fn, rid):
        try:
            fn()
            unit(label, rid, "no-refusal")
        except Refuse as e:
            unit(label, rid, str(e).split(":")[0], str(e)[:110])

    steady = [17.4] * 45
    unit("CLEAN_steady_window_above_the_floor_is_CLEAR", "CLEAR",
         gate(steady, 16.0, 63.0)["verdict"])
    fires("R1 fires on 19 samples", lambda: gate([17.4] * 19, 16.0, 63.0), "R1_COUNT")
    unit("R1_boundary_20_samples_does_NOT_fire", "CLEAR",
         gate([17.4] * 20, 16.0, 63.0)["verdict"])
    fires("R2 fires on a 29 s window", lambda: gate(steady, 16.0, 29.0), "R2_SPAN")
    fires("R3 fires on ONE excursion in 45", 
          lambda: gate([17.4] * 44 + [1.96], 16.0, 63.0), "R3_EXCURSION")
    # the statistic that matters: a HEALTHY-LOOKING median with a bad minimum
    bimodal = [17.4] * 26 + [2.0] * 19
    fires("R3 fires on median 17.4 with min 2.0 -- THE WRONG-STATISTIC CASE",
          lambda: gate(bimodal, 16.0, 63.0), "R3_EXCURSION")
    unit("the bimodal window's MEDIAN would have PASSED a median gate", True,
         sorted(bimodal)[len(bimodal) // 2] >= 16.0,
         "median=%.2f -- which is exactly why the median is not the statistic"
         % sorted(bimodal)[len(bimodal) // 2])
    falling = [20.0 - 0.08 * i for i in range(45)]
    unit("R4_mutation_applied__window_never_crosses_the_floor", True,
         min(falling) >= 16.0, "min=%.2f" % min(falling))
    fires("R4 fires on a falling window that has NOT yet crossed",
          lambda: gate(falling, 16.0, 63.0, arm_wall_s=3600), "R4_TREND")
    unit("R4 does NOT fire on the same window with no arm budget given", "CLEAR",
         gate(falling, 16.0, 63.0)["verdict"])
    n_ok = sum(1 for u in units if u["ok"])
    for u in units:
        sys.stdout.write("  %-62s %s  %s\n" % (u["u"], "ok" if u["ok"] else "FAILED",
                                               u["d"] or ("want=%r got=%r" % (u["w"], u["g"]))))
    sys.stdout.write("D7FR_MEMGATE_SELFTEST units=%d passed=%d failed=%d\n"
                     % (len(units), n_ok, len(units) - n_ok))
    return 0 if n_ok == len(units) else 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--replay", help="file of MemAvailable GiB readings, one per line")
    ap.add_argument("--floor", type=float)
    ap.add_argument("--span", type=float, help="the window's wall span in seconds")
    ap.add_argument("--arm-wall", type=float, default=None)
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not (a.replay and a.floor and a.span):
        sys.stderr.write("D7FR_MEMGATE REFUSED need --replay --floor --span\n")
        sys.exit(2)
    try:
        r = gate(_read(a.replay), a.floor, a.span, a.arm_wall)
    except Refuse as e:
        sys.stderr.write("D7FR_MEMGATE REFUSED %s\n" % e)
        sys.exit(2)
    sys.stdout.write("D7FR_MEMGATE CLEAR %s\n" % json.dumps(r, sort_keys=True))
    sys.exit(0)


if __name__ == "__main__":
    main()
