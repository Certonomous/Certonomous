"""Citable literature reference values for the F5a cylinder Reynolds ladder.

Every number here was read off a fetched primary (or, where noted, a
secondary table that itself cites and reproduces the primary) source during
this task -- none is from memory alone, and none is fabricated. Where a
value could not be independently verified, that is stated explicitly at the
point of use rather than silently omitted.

Primary sources actually fetched and read in this task:

  [Parnaudeau2008] Parnaudeau, P., Carlier, J., Heitz, D., Lamballais, E.
    (2008) "Experimental and numerical studies of the flow over a circular
    cylinder at Reynolds number 3900", Phys. Fluids 20, 085101.
    https://doi.org/10.1063/1.2957018
    Table II (mean flow parameters) read directly:
      PIV (exp.):     Re=3900  Lr/D=1.51  Umin/Uc=-0.34  L(u'u')/D=0.87
      HWA (exp.):     Re=3900  St=0.208+/-0.002
      HR LES (present):Re=3900 St=0.208+/-0.001  Lr/D=1.56  Umin/Uc=-0.26
      Lourenco & Shih (1993), their ref 5:      Re=3900  Lr/D=1.18  Umin/Uc=-0.25
      Kravchenko & Moin (2000), their ref 16 case II: Re=3900 St=0.210 Lr/D=1.37 Umin/Uc=-0.35
      Ma et al. (2000), their ref 8 case II:    Re=3900  St=0.219  Lr/D=1.59
      Dong et al. DNS, their ref 12:            Re=3900  St=0.203  Lr/D=1.36  Umin/Uc=-0.291

  [HeZhaoWan2018] He, J., Zhao, W., Wan, D. "Numerical Calculations for
    Smooth Circular Cylinder Flow at 3900 Reynolds Numbers with SST-IDDES
    Turbulence Model", ICCM2018, Shanghai Jiao Tong Univ.
    https://www.sci-en-tech.com/ICCM2018/PDFs/3403-10945-1-PB.pdf
    Table 1 (Overall flow parameters of the flow past a circular cylinder,
    Re=3900) read directly -- columns Cd, -Cpb, St, Lrec/D, theta_sep(deg):
      PIV Exp. of Lourenco & Shih (1993):  Cd=0.99  -Cpb=0.88  St=0.215  Lrec/D=1.33  theta=89
      DNS of Ma et al. (2000):             Cd=0.84             St=0.220  Lrec/D=1.59
      SST-DES of Xu et al. (2010):         Cd=1.08             St=0.220  Lrec/D=0.98
      DNS of Frederic & Tremblay (2002):   Cd=1.03  -Cpb=0.93  St=0.220  Lrec/D=1.30  theta=85.7
      LES of Frederic & Tremblay (2002):   Cd=1.14  -Cpb=0.99  St=0.210  Lrec/D=1.04  theta=87.3
      LES of Kravchenko & Moin (2000):     Cd=1.04  -Cpb=0.94  St=0.210  Lrec/D=1.35  theta=88.0
      Present (SJTU) SST-DDES:             Cd=0.99  -Cpb=0.83  St=0.207  Lrec/D=1.27  theta=87.1
      Present (SJTU) SST-IDDES:            Cd=0.97  -Cpb=0.87  St=0.215  Lrec/D=1.20  theta=86.5

  [Roshko1961] Roshko, A. (1961) "Experiments on the flow past a circular
    cylinder at very high Reynolds number", J. Fluid Mech. 10, 345-356.
    Web-search-confirmed (secondary summary, primary paywalled): subcritical/
    supercritical Strouhal plateau St ~ 0.2 for 300 <~ Re <~ 3x10^5; at very
    high Re (transcritical, R > 3.5e6) Cd rises to a constant ~0.7 and
    St -> 0.27. Used here ONLY for the qualitative transcritical anchor, not
    quoted as a point value at any ladder rung (no ladder rung reaches
    Re=3.5e6).

  [Achenbach1968] Achenbach, E. (1968) "Distribution of local pressure and
    skin friction around a circular cylinder in cross-flow up to
    Re=5x10^6", J. Fluid Mech. 34, 625-639.
    Web-search-confirmed (secondary summaries of the primary, which is
    paywalled): drag coefficient falls from Cd=1.15 at Re=1.5e5 to Cd=0.25
    at Re=4e5 (the drag crisis), i.e. critical transition centred in
    2e5-4e5; subcritical plateau (Re ~1e3-1e5) Cd ~ 1.15-1.2; supercritical
    plateau (Re ~4e5-3.5e6) Cd stays low, ~0.2-0.3.

  [Williamson1996] Williamson, C.H.K. (1996) "Vortex Dynamics in the
    Cylinder Wake", Annu. Rev. Fluid Mech. 28, 477-539. Web-search-confirmed:
    wake is 2D/laminar-periodic for 49<=Re<=190; three-dimensionality
    (mode A) onsets at Re~188-190; already cited in
    sdk/workflows/cylinder_vortex_shedding.py for the Re=100-200 family.

  [JiangCheng2017] Jiang, H., Cheng, L. (2017) "Strouhal-Reynolds number
    relationship for flow past a circular cylinder", J. Fluid Mech. 832,
    170-188. https://doi.org/10.1017/jfm.2017.679 (fetched as the UWA
    accepted-manuscript repository copy). DIRECTLY ON POINT for the F5a
    Re=1000/2000 rungs: this is a 2D-vs-3D DNS study run with OpenFOAM (the
    same code family used throughout this task) for Re<=1000. Their Fig. 2
    plots BOTH the raw St_2D(Re) and St_3D(Re) curves (open-square/x markers,
    read directly off the published figure -- a plot reading, not a
    tabulated number, so treated with +/-0.005 reading uncertainty):
      St_2D(Re=1000) ~ 0.236-0.238 (2D DNS keeps climbing past Re~300,
        no plateau reached by Re=1000)
      St_3D(Re=1000) ~ 0.208-0.210 (3D DNS is close to flat from Re~300
        onward, consistent with the Re=3900 3D cluster in RE3900 above)
    The paper's own stated mechanism (their abstract): "the drop in St*
    [wake Strouhal number, and by extension St] ... for a 3D flow ... is due
    to the decrease in the separating velocity and the increase in the wake
    width for a 3D flow" -- i.e. this IS the citable, mechanistic
    documentation of the 2D-vs-3D Strouhal bias direction and, uniquely
    among the sources gathered in this task, an actual point-level 2D
    reference curve to gate a 2D run against, rather than only a 3D
    reference that a 2D run is expected to deviate from.

  [FeyKonigEckelmann1998] Fey, U., Konig, M., Eckelmann, H. (1998) "A new
    Strouhal-Reynolds-number relationship for the circular cylinder in the
    range 47<Re<2x10^5", Phys. Fluids 10, 1547-1549. Web-search-confirmed
    (could not fetch the exact Sr*/m regime coefficients within this task's
    effort budget -- NOT independently verified to a point formula here):
    a piecewise Sr = Sr* + m/sqrt(Re) law exists, with a regime change
    (shear-layer instability) reported near Re~1300. Used only to support
    the qualitative statement that the St~0.2 plateau is not perfectly flat
    across 1e3-1e4; no point numbers from this paper are quoted as gate
    references (the gate instead uses the Roshko plateau band, which IS
    corroborated by the Parnaudeau/He-Zhao-Wan point measurements above).

Everything below is either a literature number with a citation key above, or
explicitly marked as this task's own engineering judgement (banding /
tolerance), never presented as if it were a literature value.
"""

# Strouhal plateau, subcritical regime, 300 <~ Re <~ 2e5: St ~ 0.20-0.22
# [Roshko1961] qualitative plateau; central value/band corroborated by the
# tight Re=3900 cluster in [Parnaudeau2008]/[HeZhaoWan2018] (0.203-0.220).
ST_PLATEAU_CENTER = 0.21
ST_PLATEAU_LO = 0.19
ST_PLATEAU_HI = 0.23

# Subcritical Cd plateau (Re ~1e3-1e5): ~1.15-1.2 [Achenbach1968].
CD_SUBCRITICAL_LO = 1.0
CD_SUBCRITICAL_HI = 1.3

# 2D-DNS Strouhal reference curve [JiangCheng2017], read off their Fig. 2 --
# the CORRECT apples-to-apples reference for a 2D solve at Re=1000/2000 (the
# 3D plateau above is NOT the right target here; the whole point of this
# rung is that 2D and 3D genuinely disagree, by a documented, physical
# mechanism, not by solver error). Values at Re=2000 are an extrapolation
# beyond the paper's own Re<=1000 range (stated as such, not fabricated as
# a point reading) -- St_2D is still visibly rising with Re at their upper
# limit (Re=1000), with no sign of plateauing, so Re=2000 is given as a
# wide, explicitly-extrapolated band rather than a point value.
ST_2D_DNS_REFERENCE = {
    1000: {"lo": 0.230, "hi": 0.240, "center": 0.237,
          "source": "JiangCheng2017 Fig.2 St_2D curve read at Re=1000, "
                    "+/-0.005 plot-reading uncertainty"},
    2000: {"lo": 0.225, "hi": 0.260, "center": 0.24,
          "source": "JiangCheng2017 Fig.2 St_2D trend EXTRAPOLATED past "
                    "their Re<=1000 upper limit (still rising, not "
                    "plateaued, at Re=1000) -- wide band, explicitly not "
                    "a point reading"},
}

RE3900 = {
    "strouhal": {
        "center": 0.208, "lo": 0.203, "hi": 0.220,
        "source": "Parnaudeau et al. 2008 HWA experiment St=0.208+/-0.002 "
                  "(HR LES 0.208+/-0.001); band spans Dong et al. DNS 0.203 "
                  "to Ma et al. DNS 0.219 / He-Zhao-Wan table 0.207-0.220",
    },
    "cd": {
        "center": 0.99, "lo": 0.84, "hi": 1.14,
        "source": "He/Zhao/Wan Table 1: Lourenco&Shih PIV exp Cd=0.99 "
                  "(and Norberg ~0.98, web-search-confirmed only, not "
                  "independently fetched); LES/DNS range 0.84 (Ma DNS) to "
                  "1.14 (Frederic&Tremblay LES), consensus ~0.98-1.04",
    },
    "cpb": {  # magnitude of base pressure coefficient, -Cpb, positive
        "center": 0.90, "lo": 0.83, "hi": 0.99,
        "source": "He/Zhao/Wan Table 1: -Cpb spans 0.83 (present SST-DDES) "
                  "to 0.99 (Frederic&Tremblay LES); Lourenco&Shih exp 0.88, "
                  "Kravchenko&Moin LES 0.94",
    },
    "lr_over_d": {
        "center": 1.40, "lo": 0.98, "hi": 1.66,
        "source": "Parnaudeau2008 Table II (PIV 1.51, HR LES 1.56, "
                  "Kravchenko&Moin 1.37, Lourenco&Shih 1.18(short, flagged "
                  "as likely early-transition-contaminated by both "
                  "Beaudan&Moin and Kravchenko&Moin), Ma et al. 1.59, "
                  "Dong DNS 1.36) union He/Zhao/Wan Table 1 (LES 1.04-1.35, "
                  "DES/DDES 0.98-1.27); this is a genuinely wide literature "
                  "band, reported honestly rather than narrowed artificially",
    },
    "note_2d_urans_bias": (
        "2D URANS at Re=3900 is documented in the literature (e.g. the "
        "Franke & Frank 2002 LES-vs-experiment discussion cited inside "
        "Parnaudeau et al. 2008, and the general LES-vs-URANS literature "
        "summarized in the He/Zhao/Wan DES/DDES table above) to "
        "OVER-PREDICT mean drag and UNDER-PREDICT recirculation-bubble "
        "length relative to 3D LES/experiment, because a 2D solve cannot "
        "represent the spanwise vortex stretching (mode-A/mode-B "
        "instabilities, Williamson 1996) that shortens the bubble and "
        "redistributes momentum in the real 3D wake. This task did NOT "
        "obtain a citable POINT number for the 2D-URANS Cd/Lr bias at "
        "Re=3900 specifically (the Young & Ooi 2007 comparative LES/URANS "
        "paper that directly targets this could not be fetched past its "
        "abstract within this task's effort budget) -- the DIRECTION of "
        "the bias is citable and well documented; the MAGNITUDE banding "
        "used in the F5a gate below is this task's own engineering "
        "judgement, stated as such."
    ),
}

# Achenbach 1968 drag-crisis anchors used at Re=1e5 and Re=1e6.
DRAG_CRISIS = {
    "subcritical_cd": {"lo": 1.0, "hi": 1.3, "source": "Achenbach1968, "
        "plateau Cd~1.15-1.2 for Re~1e3-1e5 (web-search-confirmed secondary "
        "summary of the primary, which is paywalled)"},
    "critical_transition_re_range": (1.5e5, 4e5),
    "cd_before_crisis": 1.15,   # Achenbach1968, at Re=1.5e5
    "cd_after_crisis": 0.25,    # Achenbach1968, at Re=4e5 (minimum)
    "supercritical_cd_band": (0.2, 0.4),
    "transcritical_cd": 0.7,    # Roshko1961, Re>3.5e6, St->0.27
    "source": "Achenbach 1968 (JFM 34, 625-639) + Roshko 1961 (JFM 10, "
              "345-356), both web-search-confirmed secondary summaries of "
              "paywalled primaries -- see module docstring",
}
