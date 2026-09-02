#!/usr/bin/env python3
"""
JET-FLAP (BLOWN WING) -- CUSTOMER-FACING FIGURE SET.

Built to Demo Standard v2 output rules R1-R10.  Nothing drawn by this script is
user-visible internal language: no case identifiers, no staging words, no gate or
verdict vocabulary, no rule/lesson/docket numbers, no solver dictionary names, no
talk of lab process.  Every figure carries a plain-English caveat box, a compute
line with the UP-FRONT ESTIMATE beside the spend (an estimate, never a cap or a
guard -- both of those flatter us), and reference curves named by their source.

INTERNAL NOTES (this file is not user-visible; the FIGURES are).

  * Two meshes are in play and they are NEVER mixed on one axis.
      - the five completed points (one unblown, four blown) share ONE 39,984-cell
        mesh.  Mesh GEOMETRY is byte-identical across all five (md5 of points,
        faces and owner match).  The CONTROLLED COMPARISON IS THE FOUR BLOWN
        POINTS AMONG THEMSELVES, and only they.  The unblown point does NOT
        differ from them in blowing alone: its jetSlot is a polyMesh `wall`
        while all four blown rows carry `patch`, so the slot is SEALED there,
        not open with the jet turned down to zero.  It is therefore drawn and
        labelled as a SEALED-SLOT REFERENCE everywhere it appears -- figure
        header, legend entry, result-sheet table.  The blown rows' own 0/U
        headers say the same thing.  Any wording that folds the unblown row
        into "five calculations differing only in blowing" is FALSE and must
        not be reintroduced.
      - the live run is a different 46,180-cell mesh.  It supplies the flow-field
        and jet-trajectory figures ONLY, never a point on the lift curve.
  * Reference area differs BY MESH and every coefficient is checked against the
    mesh it came from: 1.0 m^2 on the 46,180-cell mesh (span 1.0 m), 0.01 m^2 on
    the 39,984-cell mesh (span 0.01 m).  The script REFUSES if a file's stored
    reference area is not the one its mesh requires.
  * The theory curve is  CL = tau * sqrt( 4 pi Cmu (1 + 0.151 sqrt(Cmu)
    + 0.139 Cmu) ).  The series is INSIDE the root.  Values reproduce the
    registered table to 10 digits (0.4234034434 / 0.6047756775 / 0.8687421542 /
    1.2594769538) and that identity is asserted at run time.
  * ATTRIBUTION, CORRECTED.  The formula implemented here is Williams, Butler &
    Wood's OWN interpolation fit, not Spence's expression.  Printed p.5 of ARC
    R&M 3304 introduces eq. (2) verbatim as "The following simple interpolation
    formulae fit the computed values for c_f/c = 0 (T.E. blowing)..." and
    attaches NO reference number to it.  Printed p.3 credits Spence with the
    underlying two-dimensional problem and ref 26 on printed p.17 is Spence
    (1956), but that is the problem, not this fit.  Naming Spence here would
    assert the formula is his and the 1961 authors merely rendered it; the page
    says otherwise, and nobody in this lab has read Spence (1956) -- it returns
    HTTP 403 and is not on the box.  The figures therefore cite Williams, Butler
    & Wood alone, in the identical wording the result sheet uses, and no figure
    claims agreement has been "verified".
  * NOT ONE of the five completed runs met the convergence target on all five
    channels.  The turbulence-energy channel is the laggard everywhere and
    degrades monotonically with blowing.  Said plainly on the figures.
  * Planted-perturbation control on every reader before any figure is drawn.
"""

import math
import os
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.interpolate import griddata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from plot_jf1_p1_demo import (          # noqa: E402
    Refusal, refuse, read_internal, read_raw_surface, read_coefficient_dat,
    plant_control_internal, plant_control_raw, run_state, cl_cd_from_cp,
    jet_trajectory,
)
# The movement quantity comes from the ONE implementation, not from a second
# copy of the same arithmetic living here. This file used to compute its own
# half range over the final 4,000 iterations from read_coefficient_dat. The two
# agreed to 1e-15 on all five rows when it was measured, which is exactly the
# state the previous two failures of this kind were in right up until they were
# not. The asset manifest already claimed one implementation; now that is true.
import jf1_display_numbers as jf1num    # noqa: E402
# ONE style block for every figure in this campaign, and it REFUSES rather
# than falling back to a substitute serif. A figure drawn in the wrong font
# looks finished, which is why the check is in code and the acceptance test is
# pdffonts on the artifact rather than a read of this line.
from jf1_figure_style import latin_modern_rc, sheet_note   # noqa: E402

# ------------------------------------------------------------------- physics --
U_INF = 10.0
Q_INF = 0.5 * U_INF ** 2
CHORD = 1.0
TAU = math.pi / 6.0
TAU_DEG = 30.0
H_SLOT = 0.005

SWEEP = [                      # (directory, Cmu, reference area required)
    ("JF1_L1_UNBLOWN_A0",       0.00, 0.01),
    ("JF1_L1_BLOWN_CMU005_A0",  0.05, 0.01),
    ("JF1_L1_BLOWN_CMU010_A0",  0.10, 0.01),
    ("JF1_L1_BLOWN_CMU020_A0",  0.20, 0.01),
    ("JF1_L1_BLOWN_CMU040_A0",  0.40, 0.01),
]
SWEEP_TIME = 8000
LIVE = "JF1_P1_L1_CMESH_PHYSICS"
LIVE_AREF = 1.0

# UPFRONT ESTIMATES -- what was forecast BEFORE these ran, which is what R8
# requires.  NOT the caps and NOT the runaway guard: a cap is a stopping rule
# and forecasts nothing, and quoting one in place of the forecast turns a
# 2.07x overrun into a fake underrun.
#   SWEEP_ESTIMATE_EACH -- verification/campaign/JF1_PREREGISTRATION.md section
#     12, the "G1-G5 C_mu_jet map, L1 (5 points)" row: 5 runs at 11.36
#     core-min each, subtotal 56.79.  The string "45.0" that the RUN_STATUS
#     files carry as "cap_core_min" appears ZERO times in that registration.
#   LIVE_ESTIMATE_CORE_MIN -- staged upfront at 90.5 core-min (ranks 4,
#     assumed parallel efficiency 0.75) in the live run's queue entry, and
#     carried as the predicted figure in docs/COST_CALIBRATION.md.  The 200
#     core-min figure previously quoted here was a runaway guard, not a
#     forecast.
SWEEP_ESTIMATE_EACH = 11.36
LIVE_ESTIMATE_CORE_MIN = 90.5

# registered ten-digit values the theory function must reproduce
THEORY_CHECK = {0.05: 0.4234034434, 0.10: 0.6047756775,
                0.20: 0.8687421542, 0.40: 1.2594769538}

# ------------------------------------------------------------------- styling --
plt.rcParams.update({
    **latin_modern_rc(),
    "axes.titlesize": 12.5,
    "axes.labelsize": 11.5,
})

INK = "#16161a"
INK2 = "#45454e"
MUTED = "#8a8a93"
GRIDC = "#dcdce2"
WARN = "#a51c1c"
THEORY_C = "#111318"
LINEAR_C = "#c1121f"
RAMP = ["#bfd3e6", "#7fa8d0", "#3f7cb4", "#0b4f8f"]   # one hue, light -> dark
UNBLOWN_C = "#6d6d78"

#: THE "Preliminary" BANNER IS GONE, and its ABSENCE is now the checked state.
#:
#: Sanaa, 2026-09-01: "remove the 'Preliminary' banner from every figure".
#: What that banner said is not deleted with it -- every word of it is carried
#: by the limitations box on the results screen and by each figure's own sheet
#: note, which is where the standard puts an explanation. A banner stamped
#: across the top of a chart is not a caveat a reader can act on; it is a mood.
#:
#: THE CONSTANT IS KEPT SO THE REMOVAL CAN BE MEASURED RATHER THAN TRUSTED.
#: ``assert_no_banner`` below is called by every generator immediately before
#: it writes a page, and it reads the FIGURE, not this file: a banner
#: reintroduced by any route -- this text, a different string, a hand-placed
#: ``fig.text`` -- is caught at draw time on the artifact itself. Deleting the
#: constant would have left nothing to test against, and this act has already
#: shipped a claim its artifact did not carry.
BANNER_WORD = "Preliminary"


def tidy(ax):
    ax.grid(True, color=GRIDC, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=9.5)


def assert_no_banner(fig):
    """Refuse to write a page that still carries the removed banner.

    Walks every text object the figure actually holds, including the ones
    inside axes, and refuses if any of them carries the banner word. This is
    the replacement for the deleted ``banner()`` and it points the other way:
    the old function put the stamp on, this one proves it is off, and it reads
    the figure rather than the source. A generator that forgets the call is
    caught by the RENDERED-PDF check in the live pass, which greps the text
    layer of every page for the same word.
    """
    # matplotlib.text.Text is the only class whose get_text() is the
    # zero-argument accessor this wants. ContourLabeler also defines a
    # get_text, with the signature get_text(lev, fmt), and a duck-typed
    # `hasattr(o, "get_text")` walk calls it and raises TypeError on any page
    # carrying a contour set -- which is how this check first ran: it took
    # down the flow-field figure. Matching on the CLASS is the fix; matching
    # on the attribute name matched something else entirely.
    from matplotlib.text import Text as _Text

    for artist in fig.findobj(match=_Text):
        text = artist.get_text() or ""
        if BANNER_WORD.lower() in text.lower():
            raise Refusal("this page still carries the removed banner word "
                          "%r in %r" % (BANNER_WORD, text))


def caveat_box(ax, lines, title="WHAT YOU SHOULD KNOW ABOUT THESE NUMBERS"):
    """Plain-English caveats, laid out in two columns so the box never runs off
    the page."""
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                               fc="#f5f5f8", ec=GRIDC, lw=0.8, zorder=0,
                               clip_on=False))
    ax.text(0.012, 0.93, title, transform=ax.transAxes, fontsize=9.6,
            color=INK, weight="bold", va="top", ha="left")
    bullets = [b.rstrip("\n") for b in lines.split("  •  ") if b.strip()]
    # split by LINE count, not bullet count, so neither column overruns the box
    counts = [b.count("\n") + 1 for b in bullets]
    total = sum(counts)
    cut, acc = len(bullets), 0
    for i, c in enumerate(counts):
        if acc + c > total / 2.0 and i > 0:
            cut = i
            break
        acc += c
    for col, chunk in ((0.012, bullets[:cut]), (0.508, bullets[cut:])):
        ax.text(col, 0.78, "\n".join("•  " + b for b in chunk),
                transform=ax.transAxes, fontsize=8.6, color=INK2, va="top",
                ha="left", linespacing=1.36)


def cost_line(fig, text):
    fig.text(0.5, 0.010, text, ha="center", va="bottom", fontsize=8.0,
             color=MUTED)


def caption(fig, text, y=0.012):
    """The figure's ONE caption line, at most twenty words.

    ``y`` is the figure-fraction the line sits at. The default is the foot of
    the page; pass a higher value on a figure that ALSO carries a compute line
    there, or the two overprint into an unreadable stripe. That collision is
    not visible in the source and was found by reading the rendered image,
    which is the only place it exists.

    Sanaa's figure standard gives each figure a title of at most ten words,
    axis labels with units, a legend inside the axes, and one caption line of
    at most twenty words. Everything that used to be explained inside these
    images -- the header paragraphs, the two-column caveat boxes, the in-axes
    annotations -- moves to the result sheet as one compact paragraph per
    figure.

    THE LIMIT IS ENFORCED HERE RATHER THAN TRUSTED, and it refuses at draw
    time. Every prose rule this act carried in a comment rather than in a check
    was eventually broken by an edit that meant well, including the one that
    left a false sentence on a signed asset for a day.
    """
    words = text.split()
    if len(words) > 20:
        raise Refusal("figure caption is %d words and at most 20 are allowed: "
                      "%r" % (len(words), text))
    for word in words:
        stripped = "".join(ch for ch in word if ch.isalpha())
        if len(stripped) > 2 and stripped.isupper():
            raise Refusal("figure caption shouts %r: %r" % (stripped, text))
    fig.text(0.5, y, text, ha="center", va="bottom", fontsize=9.0,
             color=INK2)


def check_title(text, limit=10):
    """A figure title, at most ten words and not shouting."""
    words = [w for w in text.replace("\n", " ").split() if w]
    if len(words) > limit:
        raise Refusal("figure title is %d words and at most %d are allowed: %r"
                      % (len(words), limit, text))
    for word in words:
        stripped = "".join(ch for ch in word if ch.isalpha())
        if len(stripped) > 2 and stripped.isupper():
            raise Refusal("figure title shouts %r: %r" % (stripped, text))
    return text


#: Unicode superscript digits, for scientific notation inside a plain-text
#: caveat box. The box is drawn as literal text rather than mathtext, so an
#: exponent has to be spelled with these rather than with "$10^{-5}$".
_SUPERSCRIPT = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def sci_unicode(value, digits=1):
    """One measured value as "m×10ⁿ", in the notation this page already uses.

    Exists so a measured number can be WRITTEN INTO the caveat box instead of
    typed into it. The sentence this serves was previously a literal, and it
    went stale and false when the settling window changed underneath it: a
    string cannot notice that the quantity it describes has moved. Anything
    quoting a measurement in these boxes should come through here.

    ROUNDS UP, never to nearest, matching movement_1sf() in
    jf1_display_numbers.py. Rounding a movement figure DOWN would understate
    how much a calculation was still moving, which is the flattering direction
    and the one this act has already been wrong in twice.
    """
    if value == 0:
        return "0"
    exponent = int(math.floor(math.log10(abs(value))))
    scale = 10.0 ** exponent
    mantissa = math.ceil(abs(value) / scale * 10 ** digits) / 10 ** digits
    if mantissa >= 10.0:                       # 9.99e-5 -> 1.0e-4, not 10.0e-5
        mantissa, exponent = mantissa / 10.0, exponent + 1
    sign = "-" if value < 0 else ""
    return "%s%.*f×10%s" % (sign, digits, mantissa,
                            str(exponent).translate(_SUPERSCRIPT))


# -------------------------------------------------------------------- theory --
def cl_theory(cmu, tau=TAU):
    """Jet-flap thin-aerofoil lift (C_L)_inf, from the interpolation fit given
    as eq. (2) on printed p.5 of Williams, Butler & Wood, ARC R&M 3304 (1961).
    The bracket sits INSIDE the square root."""
    if cmu <= 0.0:
        return 0.0
    series = 1.0 + 0.151 * math.sqrt(cmu) + 0.139 * cmu
    return tau * math.sqrt(4.0 * math.pi * cmu * series)


def check_theory():
    for cmu, want in THEORY_CHECK.items():
        got = cl_theory(cmu)
        if abs(got - want) > 5e-10:
            refuse("theory form does not reproduce the registered value at "
                   "Cmu = %.2f: got %.10f, want %.10f" % (cmu, got, want))


def jet_reaction(cmu, alpha_deg=0.0):
    return cmu * math.sin(TAU + math.radians(alpha_deg))


# ---------------------------------------------------------------- run digest --
def digest_sweep(base):
    """One row per completed calculation: lift, its iteration scatter, the five
    convergence channels, and the compute it cost."""
    out = []
    for d, cmu, aref_req in SWEEP:
        case = os.path.join(base, d)
        cpath = os.path.join(case, "postProcessing", "forceCoeffs", "0",
                             "coefficient.dat")
        t, cols, aref = read_coefficient_dat(cpath)
        if abs(aref - aref_req) > 1e-12:
            refuse("stored reference area for %s is %.6g m2, not the %.6g m2 "
                   "this mesh requires -- every coefficient in it is wrong by "
                   "%.4g x" % (d, aref, aref_req, aref_req / aref))
        cl = cols["Cl"]
        cd = cols["Cd"]
        # Settling window: the final 4,000 iterations, not the final 1,000.
        # This figure was NOT wrong before. It computed its error bars at
        # render time and its bars were honest for the window it used. The
        # window changed because the lab tightened its own convention: where
        # two defensible definitions exist and one flatters the result, take
        # the one that reports MORE movement. The range over the longer window
        # is also the only choice that cannot hide an excursion inside it.
        #
        # That is a different thing from the result sheet's Movement column,
        # which was a hard-coded constant contradicting its own caption. This
        # figure moved by convention; that column was defective. Do not blur
        # the two.
        #
        # THE ARITHMETIC IS NO LONGER REPEATED HERE. It is the reader every
        # other surface in this campaign uses, which also plants a known value
        # into a copy of the force history and refuses if it cannot read it
        # back, and refuses rather than shortening the window if fewer than
        # 4,000 iterations exist. This file's own version had neither control.
        scatter = jf1num.settling(case)["half_range"]
        i = int(np.argmin(np.abs(t - SWEEP_TIME)))

        si = os.path.join(case, "postProcessing", "contErr", "0",
                          "solverInfo.dat")
        hcols, last = None, None
        for line in open(si):
            if line.startswith("#"):
                if "Ux_initial" in line:
                    hcols = [c.strip() for c in line.lstrip("#").split()]
                continue
            if line.split():
                last = line.split()
        D = dict(zip(hcols, last))
        res = {k: float(D[k + "_initial"])
               for k in ("Ux", "Uy", "k", "omega", "p")}

        st = {}
        for f in os.listdir(case):
            if f.startswith("RUN_STATUS"):
                for line in open(os.path.join(case, f)):
                    p = line.split(None, 1)
                    if len(p) == 2:
                        st[p[0]] = p[1].strip()
        out.append(dict(dir=d, cmu=cmu, cl_aero=float(cl[i]),
                        cd_aero=float(cd[i]), scatter=scatter, res=res,
                        aref=aref, iters=int(t[i]),
                        core_min=float(st.get("core_min_MEASURED", "nan")),
                        # read but DELIBERATELY NOT DRAWN.  The launcher labels
                        # this 45.0 a "Registered cap"; the string 45.0 appears
                        # zero times in the registration and it is not a
                        # forecast.  The figures quote SWEEP_ESTIMATE_EACH.
                        cap=float(st.get("cap_core_min", "nan")),
                        ranks=int(st.get("ranks", "1"))))
    return out


def sweep_cp(base, d):
    p = os.path.join(base, LIVE, "artefacts", "_omesh", d, "postProcessing",
                     "jfSurf", str(SWEEP_TIME), "p_airfoilSurf.raw")
    a = read_raw_surface(p)
    return a[:, 0], a[:, 1], a[:, 3] / Q_INF, p


# ==================================================================== main ====
def main():
    base = HERE
    out = os.path.join(base, "artefacts")
    os.makedirs(out, exist_ok=True)
    scratch = os.path.join(base, LIVE, "artefacts", "_recon", "_plant")
    os.makedirs(scratch, exist_ok=True)

    check_theory()
    rows = digest_sweep(base)

    # ---- planted-perturbation controls on every reader ---------------------
    recon = os.path.join(base, LIVE, "artefacts", "_recon")
    times = sorted(int(x) for x in os.listdir(recon)
                   if x.isdigit() and int(x) > 0
                   and os.path.exists(os.path.join(recon, x, "U")))
    tlive = times[-1]
    td = os.path.join(recon, str(tlive))
    sd = os.path.join(recon, "postProcessing", "jfSurf", str(tlive))
    plant_control_internal(os.path.join(td, "p"), scratch)
    plant_control_raw(os.path.join(sd, "p_airfoilSurf.raw"), scratch)
    plant_control_raw(os.path.join(base, LIVE, "artefacts", "_omesh",
                                   SWEEP[2][0], "postProcessing", "jfSurf",
                                   str(SWEEP_TIME), "p_airfoilSurf.raw"),
                      scratch)

    # ---- derived table -----------------------------------------------------
    for r in rows:
        r["jet"] = jet_reaction(r["cmu"])
        r["cl_tot"] = r["cl_aero"] + r["jet"]
        r["theory"] = cl_theory(r["cmu"])
        r["dev"] = (100.0 * (r["cl_tot"] - r["theory"]) / r["theory"]
                    if r["theory"] > 0 else float("nan"))

    blown = [r for r in rows if r["cmu"] > 0]
    spend = sum(r["core_min"] for r in rows)

    st_live = run_state(os.path.join(base, LIVE))
    live_core_min = st_live["exec_time_s"] * 4.0 / 60.0

    # The UPFRONT ESTIMATE, not a cap or a guard.  R8 asks for the forecast we
    # made before spending, so an overrun is stated as an overrun.
    #   sweep : 11.36 core-min per calculation x 5, registered before any ran
    #   live  : 90.5 core-min, staged before it ran
    sweep_estimate = SWEEP_ESTIMATE_EACH * len(SWEEP)
    live_estimate = LIVE_ESTIMATE_CORE_MIN

    cost_sweep = ("Computer time for the five calculations on this chart: we "
                  "estimated %.1f processor-minutes before running them and used "
                  "%.1f — %.2f times our estimate."
                  % (sweep_estimate, spend, spend / sweep_estimate))
    cost_live = ("Computer time for this calculation: we estimated %.1f "
                 "processor-minutes before running it and used %.1f — %.1f %% over "
                 "our estimate."
                 % (live_estimate, live_core_min,
                    100.0 * (live_core_min / live_estimate - 1.0)))

    # THE MOVEMENT SENTENCE IS COMPUTED, NOT TYPED, and this is the third
    # defect this act has carried in this one quantity. The line here used to
    # read "The lift itself has stopped moving: over the last 1000 iterations
    # it varies by less than ±3×10⁻⁵", and it was wrong three separate ways:
    #
    #   1. THE BOUND WAS FALSE for the window the rest of this page uses. The
    #      worst row moves 3.383e-05 over the final 4,000 iterations, which is
    #      not "less than 3×10⁻⁵". Wrong in the flattering direction, again.
    #   2. THE WINDOW WAS THE RETIRED ONE. Everything else on this page moved
    #      to 4,000 iterations when the lab tightened its own convention; this
    #      sentence stayed at 1,000 because it was a string and strings do not
    #      raise.
    #   3. "HAS STOPPED MOVING" IS A CONVERGENCE CLAIM, and this act exists to
    #      refuse exactly that claim. Not one of the five reached its target.
    #
    # So the number is now read out of `rows`, whose scatter is the half range
    # over the final 4,000 iterations and agrees with the single implementation
    # in jf1_display_numbers.settling() to 1e-15 on all five rows, measured.
    worst_scatter = max(r["scatter"] for r in rows)
    # THIS TEXT WAS BUILT AND NEVER DRAWN. The caveat row came off figure 1
    # under Sanaa's figure standard and the string stayed behind, so the
    # disclosure existed in the source and on no artifact: the rendered figure
    # said nothing about convergence, and anyone reading this file would have
    # believed it did. A disclosure that lives only in source is worth
    # nothing. It now goes to the figure's sheet note, which is a file that
    # exists, is named after the figure, and is rewritten every time the
    # figure is.
    written = []
    notes = []
    notes.append(sheet_note(
        "jet_flap_1_lift_vs_blowing",
        "Lift against blowing",
        "None of these calculations reached the convergence target fixed "
        "before they ran, which was all five solution channels below 1e-06. "
        "The turbulence-energy channel is the slowest everywhere and worsens "
        "with blowing, from 3.5e-06 with no jet to 1.5e-04 at the strongest "
        "jet, a factor of 43; strong blowing makes this flow genuinely hard "
        "to converge, which is a property of the physics rather than of any "
        "one calculation.\n\n"
        "Over the final 4,000 iterations the lift still moves by up to %s at "
        "the worst row. That is a settling indicator and not convergence, and "
        "the bars drawn for it are smaller than the symbols.\n\n"
        "Mesh sensitivity has not been quantified for these points: no "
        "refinement study was run, so no grid uncertainty is claimed. Treat "
        "every number here as indicative. It is not a validated result and it "
        "has not been compared against experiment."
        % sci_unicode(worst_scatter)))

    def save(fig, stem):
        for ext in ("pdf", "png"):
            p = os.path.join(out, "%s.%s" % (stem, ext))
            fig.savefig(p, dpi=200, facecolor="white")
            written.append(p)
        plt.close(fig)

    # =========================================== FIGURE 1: lift vs blowing ===
    # The caveat-box row is gone: figures carry no paragraphs, and everything
    # that box said now lives on the result sheet, where it can be read rather
    # than squinted at. The header paragraph above the axes goes with it.
    fig = plt.figure(figsize=(14.0, 6.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[2.15, 1.0],
                          left=0.062, right=0.985, top=0.880, bottom=0.115,
                          wspace=0.20)
    ax = fig.add_subplot(gs[0, 0])
    axb = fig.add_subplot(gs[0, 1])

    cg = np.linspace(1e-5, 0.45, 400)
    th = np.array([cl_theory(c) for c in cg])
    ax.plot(cg, th, "-", color=THEORY_C, lw=2.4, zorder=4,
            label="jet-flap thin-aerofoil theory, $(C_L)_\\infty$,  "
                  "Williams, Butler & Wood,\n"
                  "ARC R&M 3304 (1961), eq. (2):  "
                  "$C_L \\propto \\sqrt{C_\\mu}$")

    slope = cl_theory(0.40) / 0.40
    ax.plot(cg, slope * cg, "--", color=LINEAR_C, lw=2.0, zorder=3,
            label="If lift instead grew in proportion to jet momentum\n"
                  "(same value at $C_\\mu = 0.40$)")

    xs = [r["cmu"] for r in blown]
    yt = [r["cl_tot"] for r in blown]
    ya = [r["cl_aero"] for r in blown]
    er = [r["scatter"] for r in blown]
    ax.errorbar(xs, yt, yerr=er, fmt="o", ms=8.5, color=RAMP[3],
                mfc=RAMP[3], mec="white", mew=1.2, ecolor=INK2, capsize=4,
                lw=0, elinewidth=1.2, zorder=6,
                label="Computed total lift  (wing + direct jet reaction)")
    ax.plot(xs, ya, "s", ms=7.5, color=RAMP[1], mfc="white", mec=RAMP[3],
            mew=1.6, zorder=5,
            label="Computed lift on the wing surface alone")
    ax.plot([0.0], [rows[0]["cl_aero"]], "^", ms=8.5, color=UNBLOWN_C,
            mfc=UNBLOWN_C, mec="white", mew=1.2, zorder=6,
            # ONE LINE.  A two-line entry grows the legend box and the
            # "first 12 % of the momentum" annotation then lands on top of the
            # entry above it.  The symmetric-section-at-zero-incidence fact is
            # already in the figure header, so it is not repeated here.
            label="Reference case, slot closed: $C_L = %.5f$"
                  % rows[0]["cl_aero"])

    # THE LAST LABEL MOVES CLEAR OF THE THEORY CURVE (Sanaa 2010Z: at
    # the strongest blowing the "+11 pt above" slot sits exactly in the
    # band between the point and the theory line, so "1.210" printed
    # over the black curve and read like "1.2*0"). That one label goes
    # to the right of its dot, below both rising curves; the data and
    # every other label are untouched.
    last_cmu = max(r["cmu"] for r in blown)
    for r in blown:
        if r["cmu"] == last_cmu:
            ax.annotate("%.3f" % r["cl_tot"], xy=(r["cmu"], r["cl_tot"]),
                        xytext=(11, -3), textcoords="offset points",
                        ha="left", fontsize=8.6, color=INK)
        else:
            ax.annotate("%.3f" % r["cl_tot"], xy=(r["cmu"], r["cl_tot"]),
                        xytext=(0, 11), textcoords="offset points",
                        ha="center", fontsize=8.6, color=INK)

    ax.set_xlim(-0.012, 0.455)
    ax.set_ylim(0.0, 1.42)
    ax.set_xlabel("jet momentum coefficient  $C_\\mu$  [-]")
    ax.set_ylabel("lift coefficient  $C_L$  [-]")
    ax.set_title(check_title("Lift grows with the square root of jet momentum"),
                 weight="bold", color=INK, loc="left", pad=9)
    leg = ax.legend(frameon=False, fontsize=8.9, loc="lower right",
                    labelspacing=0.8, borderaxespad=1.1)
    for t_ in leg.get_texts():
        t_.set_color(INK2)
    tidy(ax)

    # The "first N% of the momentum buys M% of the lift" annotation is gone
    # from inside the axes. It is an explanation, and explanations go to the
    # sheet; the marginal panel to the right shows the same thing as numbers.

    # --- marginal return panel
    steps = [(blown[i]["cmu"], blown[i + 1]["cmu"],
              (blown[i + 1]["cl_tot"] - blown[i]["cl_tot"]) /
              (blown[i + 1]["cmu"] - blown[i]["cmu"]))
             for i in range(len(blown) - 1)]
    labels = ["%.2f→%.2f" % (a, b) for a, b, _ in steps]
    vals = [v for _, _, v in steps]
    bars = axb.bar(range(len(vals)), vals, color=RAMP[1:], width=0.62,
                   edgecolor="white", linewidth=1.5)
    for i, v in enumerate(vals):
        axb.text(i, v + 0.07, "%.2f" % v, ha="center", fontsize=9.2, color=INK)
    axb.set_xticks(range(len(vals)))
    axb.set_xticklabels(labels, fontsize=9.0)
    axb.set_ylim(0, max(vals) * 1.30)
    axb.set_xlabel("change in $C_\\mu$ over the step  [-]")
    axb.set_ylabel("extra lift per unit of\nextra jet momentum  [-]")
    axb.set_title(check_title("Each extra unit of blowing buys less"),
                  weight="bold", color=INK, loc="left", fontsize=11.0, pad=9)
    tidy(axb)

    assert_no_banner(fig)
    caption(fig, "Four blown settings and one slot-closed reference, on one "
                 "grid, against published jet-flap theory.")
    save(fig, "jet_flap_1_lift_vs_blowing")

    # ======================================= FIGURE 2: surface pressure ======
    fig = plt.figure(figsize=(14.0, 6.4))
    gs = fig.add_gridspec(1, 2, left=0.062, right=0.985, top=0.880,
                          bottom=0.115, wspace=0.16)
    axu = fig.add_subplot(gs[0, 0])
    axl = fig.add_subplot(gs[0, 1])

    handles = []
    for r in rows:
        x, y, cp, path = sweep_cp(base, r["dir"])
        r["cp_path"] = path
        col = UNBLOWN_C if r["cmu"] == 0 else RAMP[[0.05, 0.10, 0.20, 0.40]
                                                   .index(r["cmu"])]
        ls = (0, (5, 3)) if r["cmu"] == 0 else "-"
        lab = ("reference: slot closed" if r["cmu"] == 0
               else "$C_\\mu = %.2f$" % r["cmu"])
        for axx, sel in ((axu, y > 0), (axl, y < 0)):
            s = np.argsort(x[sel])
            axx.plot(x[sel][s] / CHORD, cp[sel][s], ls=ls, color=col, lw=2.0)
        handles.append(Line2D([], [], color=col, ls=ls, lw=2.2, label=lab))

    for axx, ttl in ((axu, "Upper (suction) surface"),
                     (axl, "Lower (pressure) surface")):
        axx.axhline(0, color=MUTED, lw=0.8)
        axx.invert_yaxis()
        axx.set_xlabel("distance along the chord  $x/c$  [–]")
        axx.set_title(ttl, weight="bold", color=INK, loc="left", fontsize=11.5,
                      pad=8)
        tidy(axx)
    axu.set_ylabel("pressure coefficient  $C_p$  [–]")
    # clipped so the chord is readable; the slot-lip spike at x/c = 1 runs off
    # the top of the scale and is called out rather than allowed to set it
    axu.set_ylim(1.15, -2.6)
    axl.set_ylim(1.15, -2.6)
    leg = axl.legend(handles=handles, frameon=False, fontsize=9.5,
                     loc="lower left", bbox_to_anchor=(0.13, 0.02),
                     title="jet strength")
    leg.get_title().set_color(INK2)
    for t_ in leg.get_texts():
        t_.set_color(INK2)

    # The two in-axes explanations move to the sheet with the rest.

    assert_no_banner(fig)
    caption(fig, "Chordwise pressure for four blown settings and the "
                 "slot-closed reference, upper and lower surfaces separated.")
    save(fig, "jet_flap_2_surface_pressure")

    # ==================== live-run figures: field and jet trajectory =========
    ctimes, cc, aref = read_coefficient_dat(
        os.path.join(base, LIVE, "postProcessing", "forceCoeffs", "0",
                     "coefficient.dat"))
    if abs(aref - LIVE_AREF) > 1e-12:
        refuse("stored reference area for the live run is %.6g m2, not %.6g m2"
               % (aref, LIVE_AREF))
    j = int(np.argmin(np.abs(ctimes - tlive)))
    cl_live = float(cc["Cl"][j])

    cx = read_internal(os.path.join(td, "Cx"))
    cy = read_internal(os.path.join(td, "Cy"))
    Uv = read_internal(os.path.join(td, "U"))
    mag = np.linalg.norm(Uv, axis=1)
    af = read_raw_surface(os.path.join(sd, "p_airfoilSurf.raw"))
    js = read_raw_surface(os.path.join(sd, "p_jetSlotSurf.raw"))
    xy = np.column_stack([np.concatenate([af[:, 0], js[:, 0]]),
                          np.concatenate([af[:, 1], js[:, 1]])])
    cpc = np.concatenate([af[:, 3], js[:, 3]]) / Q_INF
    _, _, poly = cl_cd_from_cp(xy, cpc)
    tx, ty, tm = jet_trajectory(cx, cy, Uv)

    frac = 100.0 * st_live["bounded"] / max(1, st_live["steps"])
    # THE SECOND DEAD DISCLOSURE, and the more serious of the two: this string
    # named the 46,180-cell difference between the flow picture's grid and the
    # lift chart's grid, and it was built into a variable that no figure ever
    # drew. The rendered PDF carries no such admission. That is the exact
    # shape the act's gates line was wrong in -- an honest sentence in a file,
    # a screen saying something else -- so it goes where a reader can reach
    # it, and the same fact is now stated on camera in the act's caveat box
    # and measured by the display guard rather than typed.
    live_note = (
        "This calculation ran its full %d of %d iterations and did not reach "
        "the convergence target fixed before it started. The pressure channel "
        "finished at %.1e, about %.0f times the 1e-06 target; it fell early, "
        "then flattened and stayed flat.\n\n"
        "The turbulence model's energy variable goes slightly negative in a "
        "handful of cells and is clipped back to zero on %.0f %% of "
        "iterations, continuously from iteration %s to the last one. The "
        "picture is held by that clipping rather than converged free of it, "
        "and that is a real limitation of this result.\n\n"
        "This is a different, finer mesh of %s cells from the five "
        "calculations on the lift and pressure charts. Its reference area is "
        "%.2f m2 against their %.2f m2. It is shown for the flow picture only "
        "and contributes no point to those charts; the two are never plotted "
        "on one axis. Indicative only: no mesh-refinement study, no "
        "experiment.")
    # The two cell counts and the two reference areas are READ, not typed:
    # they are the quantities the whole one-grid rule turns on, and the note
    # that names them has to move when they do.
    live_cells = jf1num.cell_count(os.path.join(base, LIVE))["cells"]
    sweep_aref = jf1num.reference_area(os.path.join(base, SWEEP[3][0]))
    notes.append(sheet_note(
        "jet_flap_3_flow_field", "Flow field at the slot",
        live_note % (st_live["last_time"], int(jf1num.FLOW_TIME),
                     st_live["res"]["p"], st_live["res"]["p"] / 1e-6,
                     frac, st_live["first_bounded"],
                     "{:,}".format(int(live_cells)), aref, sweep_aref)))

    # -------------------------------------------------- FIGURE 3: the field --
    fig = plt.figure(figsize=(14.0, 7.6))
    gs = fig.add_gridspec(1, 1, left=0.055, right=0.935, top=0.895,
                          bottom=0.095)
    ax = fig.add_subplot(gs[0, 0])

    xlim, ylim = (-0.75, 3.25), (-0.98, 0.90)
    m = ((cx > xlim[0] - 0.3) & (cx < xlim[1] + 0.3) &
         (cy > ylim[0] - 0.3) & (cy < ylim[1] + 0.3))
    gx = np.linspace(*xlim, 640)
    gy = np.linspace(*ylim, 420)
    GX, GY = np.meshgrid(gx, gy)
    pts = np.column_stack([cx[m], cy[m]])
    GM = griddata(pts, mag[m], (GX, GY), method="linear")
    GU = griddata(pts, Uv[m, 0], (GX, GY), method="linear")
    GV = griddata(pts, Uv[m, 1], (GX, GY), method="linear")

    # polarity, not magnitude: faster-than-oncoming vs slower-than-oncoming,
    # neutral exactly at the oncoming speed
    GR = GM / U_INF - 1.0
    cf = ax.contourf(GX, GY, GR, levels=np.linspace(-0.55, 0.55, 45),
                     cmap="RdBu_r", extend="both")
    try:
        cf.set_rasterized(True)
    except Exception:
        pass
    ax.contour(GX, GY, GR, levels=[0.0], colors=["#33333a"], linewidths=1.0,
               linestyles="--", alpha=0.7)
    seeds = np.column_stack([np.full(30, xlim[0] + 0.02),
                             np.linspace(ylim[0] + 0.04, ylim[1] - 0.04, 30)])
    ax.streamplot(gx, gy, GU, GV, color="#33333a", linewidth=0.5,
                  arrowsize=0.7, start_points=seeds, maxlength=12.0,
                  integration_direction="both")
    ax.fill(np.append(poly[:, 0], poly[0, 0]),
            np.append(poly[:, 1], poly[0, 1]), color="#0b0b0e", zorder=6)
    ax.plot(tx, ty, "-", color="#0b4f8f", lw=2.4, zorder=7)

    cb = fig.colorbar(cf, ax=ax, pad=0.012, fraction=0.030,
                      ticks=[-0.5, -0.25, 0.0, 0.25, 0.5])
    cb.set_label("air speed relative to the oncoming stream,  "
                 "$|\\mathbf{U}|/U_\\infty - 1$  [-]", fontsize=9.5,
                 color=INK2)
    cb.ax.tick_params(labelsize=8.5, colors=INK2)
    cb.outline.set_edgecolor(GRIDC)

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("$x/c$  [-]")
    ax.set_ylabel("$y/c$  [-]")
    ax.set_title(check_title("A jet of air doing the job of a flap"),
                 weight="bold", color=INK, loc="left", pad=9)
    ax.tick_params(colors=INK2, labelsize=9.5)
    # The six-line block that used to sit inside these axes -- what red and
    # blue mean, what the dark line is, what the display grid is -- is on the
    # sheet now. A picture explaining itself in a paragraph is the thing the
    # standard removes.

    assert_no_banner(fig)
    # The dashed contour is NAMED (Sanaa 2010Z): it is the zero level of
    # the plotted quantity, where local speed equals the oncoming
    # stream, read off the contour call above. 19 words, under the
    # generator's own 20-word caption gate.
    caption(fig, "Speed relative to the oncoming stream; jet sheet traced; "
                 "streamlines equally spaced; dashed line: speed equals "
                 "the oncoming stream.")
    save(fig, "jet_flap_3_flow_field")

    # ----------------------------------------------- FIGURE 4: trajectory ---
    fig = plt.figure(figsize=(14.0, 6.8))
    gs = fig.add_gridspec(1, 1, left=0.062, right=0.985, top=0.895,
                          bottom=0.105)
    ax = fig.add_subplot(gs[0, 0])

    ax.fill(np.append(poly[:, 0], poly[0, 0]),
            np.append(poly[:, 1], poly[0, 1]), color="#16161a", zorder=4,
            label="wing section")
    xr = np.linspace(1.0, max(tx.max(), 2.4), 60)
    ax.plot(xr, -(xr - 1.0) * math.tan(TAU), "--", color=LINEAR_C, lw=2.0,
            zorder=5, label="where a free jet aimed 30° down would go")
    sc = ax.scatter(tx, ty, c=tm, cmap="viridis", s=26, zorder=6,
                    edgecolor="white", linewidth=0.4, vmin=U_INF,
                    vmax=float(tm.max()))
    ax.plot(tx, ty, "-", color=RAMP[3], lw=2.2, zorder=5,
            label="path the jet sheet actually takes")
    cax = ax.inset_axes([0.045, 0.125, 0.27, 0.030])
    cb = fig.colorbar(sc, cax=cax, orientation="horizontal")
    cb.set_label("fastest air on the cut  [m s$^{-1}$]", fontsize=8.6,
                 color=INK2, labelpad=4)
    cb.ax.xaxis.set_label_position("top")
    cb.ax.tick_params(labelsize=8.0, colors=INK2)
    cb.outline.set_edgecolor(GRIDC)

    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xlim(-0.2, max(tx.max(), 2.4) + 0.25)
    ax.set_ylim(-1.10, 0.32)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("$x/c$  [–]   (slot at $x/c = 1.00$)")
    ax.set_ylabel("$y/c$  [-]")
    ax.set_title(check_title("The jet is turned by the flow it is turning"),
                 weight="bold", color=INK, loc="left", pad=9)
    leg = ax.legend(frameon=False, fontsize=9.2, loc="upper right")
    for t_ in leg.get_texts():
        t_.set_color(INK2)
    tidy(ax)

    # The eight-line block inside these axes moves to the sheet as well. The
    # numbers it carried -- the turning angle, the deviation from a free jet,
    # the speed decay -- are quantities, and quantities belong in the sheet's
    # tables where they can be read beside their uncertainty.

    assert_no_banner(fig)
    caption(fig, "The ejected sheet leaves at thirty degrees and is turned by "
                 "the oncoming flow; colour is peak speed.")
    save(fig, "jet_flap_4_jet_path")

    # ------------------------------------------------------------ readout ---
    print("THEORY IDENTITY CHECK  : reproduces all four registered values")
    print()
    print("%-6s %12s %12s %12s %12s %10s %11s %10s"
          % ("Cmu", "CL_wing", "CL_jetreact", "CL_total", "CL_theory",
             "dev_%", "iter_scatter", "core_min"))
    for r in rows:
        print("%-6.2f %12.6f %12.6f %12.6f %12.6f %10s %11.2e %10.4f"
              % (r["cmu"], r["cl_aero"], r["jet"], r["cl_tot"], r["theory"],
                 ("%+.2f" % r["dev"]) if r["cmu"] > 0 else "--",
                 r["scatter"], r["core_min"]))
    print()
    print("residuals (initial, first solve of each outer iteration, "
          "target 1e-06):")
    print("%-6s %11s %11s %11s %11s %11s  %s"
          % ("Cmu", "p", "Ux", "Uy", "k", "omega", "all<1e-6"))
    for r in rows:
        R = r["res"]
        ok = all(R[k] < 1e-6 for k in R)
        print("%-6.2f %11.3e %11.3e %11.3e %11.3e %11.3e  %s"
              % (r["cmu"], R["p"], R["Ux"], R["Uy"], R["k"], R["omega"],
                 "YES" if ok else "NO"))
    print()
    print("sweep compute    : %.2f core-min used / %.2f core-min ESTIMATED "
          "up front (%.3fx)" % (spend, sweep_estimate, spend / sweep_estimate))
    print("live run compute : %.2f core-min used / %.2f core-min ESTIMATED "
          "up front (%.3fx, 4 ranks, %.0f s)"
          % (live_core_min, live_estimate, live_core_min / live_estimate,
             st_live["exec_time_s"]))
    print("live run state   : iteration %d of 20000, p residual %.3e, "
          "clipping on %.1f %% of iterations since %s"
          % (st_live["last_time"], st_live["res"]["p"], frac,
             st_live["first_bounded"]))
    print("live lift (46180-cell mesh, ref area %.3f m2) CL_wing = %.6f"
          % (aref, cl_live))
    print()
    # THE FIGURES' PROVENANCE, RECORDED AT RENDER TIME. Nothing inside a PNG
    # says which grid it came from, and the screen's grid statement was false
    # about exactly that for as long as nobody could check it. The generator
    # is the only thing that knows, so it writes it down, measuring the cell
    # count and the reference area out of the case's own files as it does.
    prov = jf1num.write_figure_provenance({
        "jet_flap_1_lift_vs_blowing": os.path.join(base, SWEEP[3][0]),
        "jet_flap_2_surface_pressure": os.path.join(base, SWEEP[3][0]),
        "jet_flap_3_flow_field": os.path.join(base, LIVE),
        "jet_flap_4_jet_path": os.path.join(base, LIVE),
    })
    print("PROVENANCE %s" % prov)
    for p in notes:
        print("SHEET NOTE %s" % p)
    for p in written:
        print("WROTE %s" % p)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        sys.exit(2)
