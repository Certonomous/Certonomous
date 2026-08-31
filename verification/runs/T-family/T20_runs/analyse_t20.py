#!/usr/bin/env python3
"""T20 -- the comparator.  Lumped-capacitance transient control with internal
generation, EXACT tier.  chtMultiRegionFoam at v2606, solid-only, ZERO fluid
regions, one 2-D rectangle, imposed h, uniform volumetric source.

============================================================================
DISCLOSURE 1 -- READ BEFORE ANY NUMBER THIS FILE PRINTS IS BELIEVED.
T20's GATED GRADING IS NO LONGER ANALYST-BLIND.
============================================================================
The pre-registered PREDICTIONS of T20_PREREGISTRATION.md section 4.5 (the six
predicted residuals) and section 5.1 (the predicted observed orders and GCIs)
HAVE BEEN READ by the lane that wrote this comparator, before this comparator
existed.  Any grading T20 produces must declare that loss of blindness on its
face, and this file is the face.

WHAT SURVIVES, AND WHY RULE 2 IS INTACT.  Every gate, threshold, band, cap and
label was frozen at commit 7b93b2c805598987ab405cb7901642d909257264, BEFORE the
predictions were read and before any solver ran in the registered run tree.  The
freeze is the document's entire evidentiary content and it is undisturbed: the
gates could not have been chosen to fit an answer that did not yet exist.  What
is lost is the weaker, separate property that the ANALYST was blind to the
expected values while writing the instrument.  That is STATED, not repaired --
it cannot be repaired, and a comparator that did not say so would be worse.

MECHANICALLY, this file does not merely promise the separation, it enforces it:
  * NO GATE NUMBER IS WRITTEN IN THIS FILE.  Every band, threshold and floor is
    PARSED OUT OF THE FROZEN DOCUMENT'S OWN BYTES at import, under a sha256 pin.
    A digest that does not reproduce is a REFUSAL, never a warning.
  * GATES and PREDICTIONS are two disjoint containers, and two SOURCE-LEVEL AST
    detectors -- each with a PLANTED CONTROL -- measure that no gating function
    ever reads PREDICTIONS and no reporting function ever reads GATES.

============================================================================
DISCLOSURE 2 -- SIX CASES RAN.  THE VERDICT MAP HAS ROWS FOR FOUR OF THEM.
============================================================================
Section 12 enumerates every row this rung may EVER produce and closes with "A
row not listed here is not a row."  `T20_LC_c` AND `T20_LC_m` APPEAR IN NO ROW:
section 9 marks both "triple only".  They are the coarse and medium levels of
V1/V2's temporal triple and they carry no verdict of their own.  A completed run
is not a graded row, and this comparator will not invent one: the implemented row
set is compared against the row ids PARSED FROM SECTION 12 and any difference is
a REFUSAL.

============================================================================
DISCLOSURE 3 -- V5 IS ABSENT AND ITS ABSENCE IS FATAL, BY REGISTRATION.
============================================================================
`T20_LC_P10` -- the planted +10 % source arm -- was NOT BUILT and cannot be built
by any current builder: `q_volumetric` lives in the rung-global `physics` block
and the case schema carries no per-case physics override, so a P10 entry would be
INERT and would emit 5000 while claiming 5500 (T20_prose_cases_7b93b2c8.json
._stopped).  Section 12 V5 registers that a refusal there makes the WHOLE RUNG
`NOT A RESULT`, and section 7 criterion (i) registers that the comparator refuses
to grade a partial rung.

SO: this comparator sweeps ALL SEVEN registered cases for completion BEFORE it
grades anything.  A missing or incomplete case makes the rung `NOT A RESULT`, no
row is graded, NO GATE JSON IS WRITTEN, and the exit code is non-zero.  THERE IS
NO FLAG THAT BYPASSES THIS.  A comparator that quietly omitted an unbuildable arm
would convert a dead lever into a clean sheet, and that is the one failure this
structure exists to make impossible.

============================================================================
DISCLOSURE 4 -- THE EXACT-TRIPLE HAZARD IS LIVE AND IS NOT ENGINEERED AROUND.
============================================================================
Section 5.2 pre-registers that a SPATIAL triple on this rung returns three
identical values and classifies EXACT, because a second-order finite-volume
Laplacian integrates the steady quadratic exactly on a uniform mesh.  Under
CLAUDE.md rule 5 clause (2) an EXACT triple is `NOT A RESULT` whatever its value.
That is a correct and honest outcome and NO TOLERANCE IS ADDED ANYWHERE to
manufacture a CONVERGING triple.  No GCI is quoted on a non-monotone triple --
roache_triple.gci_equal emits one only in the CONVERGING state.

Section 5.3 REFERS to verification, one-way and before compute, whether rule 5's
"grid triple" reads onto a temporal ladder for a rung whose spatial
discretisation is exact.  THAT REFERRAL IS OPEN.  This comparator therefore:
  * applies rule 5 in full to the TEMPORAL triple (the registered reading);
  * COMPUTES, CLASSIFIES and REPORTS the spatial triple beside every gated row,
    as section 5.3 requires, and gates on none of it;
  * prints SPATIAL_TRIPLE_REFERRAL = OPEN and states in the output what a ruling
    the other way would do (move rows ONE WAY to NOT A RESULT).
It does not resolve the referral and it does not take the lenient branch
silently.

============================================================================
EXIT CODES
============================================================================
  0  graded; gate json written
  2  REFUSE -- an instrument failed, a pin failed, or a structural check failed.
     Nothing is graded and nothing is written.
  3  RUNG NOT A RESULT -- a registered case failed completion (section 7
     criterion (i)) or V5 refused (section 12).  Nothing is graded and nothing
     is written.  The separate code is deliberate and is BORROWED, not invented:
     scripts/roache_triple.py registers EXIT_NOT_A_RESULT = 3 because "checked
     and failed the band" and "cannot be graded at all" are different facts and
     collapsing them is the L-45 error.

NO `assert` (L-332): every refusal is sys.exit().  apply_gate() is the ONLY
function that writes a verdict.  Comparators REFUSE rather than degrade
(CLAUDE.md rule 4).

============================================================================
S8 (section 10.1) -- NO SELFTEST LIMB TOUCHES A LIVE RUN TREE
============================================================================
Registered and binding: no selftest limb may read, stat, glob or assert anything
about verification/runs/T-family/T20_runs/ or any other live run tree.  Every
limb forges its own synthetic tree in a scratch directory it creates and removes.
The invariance is MEASURED, not promised, by four independent detectors:
  (S8a) the whole limb set runs TWICE in one invocation -- once against an EMPTY
        synthetic run root, once against one FULLY POPULATED with all seven cases,
        time directories, fields, logs and STATUS markers -- and the two outcome
        structures must be BYTE-IDENTICAL.
  (S8b) a filesystem watcher over the synthetic run root records every read while
        the limbs execute and must record ZERO.  Rule 3: the watcher is PLANTED
        first with a deliberate read it must see, then reset.
  (S8c) a second watcher over the LIVE T20_runs directory, allowing ONLY the
        pinned instruments, so the live tree is MEASURED untouched rather than
        asserted untouched.  This is the clause analyse_t18.py lacked: its
        `grade(HERE, ...)` limb fired on its own live tree and produced a file
        byte-identical to the real gate output.
  (S8d) a source-level detector: the name `HERE` does not occur anywhere inside
        the selftest functions, with a planted control proving it sees one.
============================================================================
"""
import argparse
import ast
import contextlib
import io
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time as _time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EXIT_OK, EXIT_REFUSE, EXIT_NOT_A_RESULT = 0, 2, 3

LAST_REFUSAL = [""]        # so a limb can measure WHICH clause fired, not just that one did


def refuse(msg):
    LAST_REFUSAL[0] = msg
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def not_a_result(msg):
    LAST_REFUSAL[0] = msg
    print("")
    print("=" * 78)
    print("RUNG VERDICT: NOT A RESULT")
    print("=" * 78)
    print(msg)
    print("No row is graded.  No gate json is written.  (exit %d)" % EXIT_NOT_A_RESULT)
    sys.exit(EXIT_NOT_A_RESULT)


# ---------------------------------------------------------------------------
# THE PINNED ARTIFACTS.  No gate number is written in this file; every one is
# parsed out of the frozen document's own bytes.  A digest that does not
# reproduce is the only mechanism by which "no gate moved" is a MEASUREMENT.
# ---------------------------------------------------------------------------
PREREG_PATH = os.path.join(REPO, "docs", "campaigns", "T-family", "T20_PREREGISTRATION.md")
PREREG_SHA256 = "915704ff385d99192540703dcbc5b793fa26e67f21b068b5cf4a7c0dfea5147a"
PREREG_COMMIT = "7b93b2c805598987ab405cb7901642d909257264"
REG_PATH = os.path.join(HERE, "T20_registered.json")
REG_SHA256 = "e04c6a64c3920e3ece42cd29924558d88fc08832b2d7062c9688b2a0956965f7"
PROSE_PATH = os.path.join(HERE, "T20_prose_cases_7b93b2c8.json")
PROSE_SHA256 = "4af2ff11a3caea60a92c7c478fc8fe699fb3a25b657a3cacbd8c9836bfae82eb"


def sha256_of(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def pin(path, want, what):
    if not os.path.isfile(path):
        refuse("the frozen artifact %s is missing at %s -- T20 grades against the frozen "
               "document and will not substitute a copy" % (what, path))
    got = sha256_of(path)
    if got != want:
        refuse("%s at %s has sha256 %s but T20 pins %s -- the file that would be read is NOT "
               "the frozen file, so no gate can be shown to be unmoved" % (what, path, got, want))
    return got


# ---------------------------------------------------------------------------
# THE FROZEN-DOCUMENT PARSER.  Every gate below is lifted from the document's
# bytes by a STRUCTURAL anchor, and a missing anchor is a REFUSAL.  Because the
# file is sha256-pinned, a parse that succeeds today succeeds forever or the pin
# fires first.
# ---------------------------------------------------------------------------
def _num(s):
    s = s.replace("−", "-").replace("±", "").replace("*", "").replace("`", "")
    return float(s.replace("%", "").replace("mK", "").replace("K", "").strip())


def _need(m, what):
    if not m:
        refuse("the frozen document does not contain the anchor for %s -- this comparator "
               "cannot invent it (section 15: 'It does not write the comparator'; and the "
               "comparator may not write a gate)" % what)
    return m


def parse_frozen(text):
    """Return (GATES, PREDICTIONS, CASES, ROW_IDS, SAMPLES).  GATES and
    PREDICTIONS are DISJOINT by construction and the caller measures that."""
    G, P = {}, {}

    # -- section 1 line 3: the sample times ---------------------------------
    m = _need(re.search(r"Sample times \*\*t = τ, 2τ, 3τ = "
                        r"([0-9]+), ([0-9]+), ([0-9]+) s exactly\*\*", text), "the sample times")
    samples = [float(m.group(i)) for i in (1, 2, 3)]

    # -- section 1 line 4: the band table -----------------------------------
    rows = re.findall(r"^\| t = (τ|2τ|3τ) \| ([0-9.]+) \| ([0-9.]+) \| "
                      r"\*\*±([0-9.]+)\*\* \|$", text, re.M)
    if len(rows) != 3:
        refuse("the frozen band table (section 1 line 4) yielded %d rows, not 3" % len(rows))
    G["rise_K"], G["band_K_tabulated"], G["band_mK_tabulated"] = {}, {}, {}
    for lbl, rise, bk, bmk in rows:
        n = {"τ": 1, "2τ": 2, "3τ": 3}[lbl]
        G["rise_K"][n] = float(rise)
        G["band_K_tabulated"][n] = float(bk)
        G["band_mK_tabulated"][n] = float(bmk)

    # THE BAND IS DEFINED, NOT TABULATED.  Section 1 line 4: "All bands are 1 % of
    # the ANALYTIC RISE".  The +-K column is a ROUNDED DISPLAY of that definition
    # (0.0189636 against 0.01896361676).  The GATE is the definition; the two
    # tabulated columns are then an INDEPENDENT CROSS-CHECK on the parse, to their
    # own display precision.  A disagreement is a REFUSAL.
    G["band_frac_of_rise"] = 0.01
    G["band_K"] = {n: 0.01 * G["rise_K"][n] for n in (1, 2, 3)}
    for n in (1, 2, 3):
        if abs(G["band_K"][n] - G["band_K_tabulated"][n]) > 5e-8:
            refuse("band cross-check failed at %d tau: 1%% of the frozen rise is %.10g K but the "
                   "frozen table prints %.10g K" % (n, G["band_K"][n], G["band_K_tabulated"][n]))
        if abs(1e3 * G["band_K"][n] - G["band_mK_tabulated"][n]) > 5e-5:
            refuse("band mK cross-check failed at %d tau: %.10g mK vs frozen %.10g mK"
                   % (n, 1e3 * G["band_K"][n], G["band_mK_tabulated"][n]))

    # -- section 1 line 4: the additional frozen bands ----------------------
    m = _need(re.search(r"temporal observed order \*\*p ∈ \[([0-9.]+), ([0-9.]+)\]\*\*", text),
              "the temporal observed-order band")
    G["p_lo"], G["p_hi"] = float(m.group(1)), float(m.group(2))
    m = _need(re.search(r"\*\*GCI_fine < ([0-9.]+) %\*\* of the rise", text),
              "the temporal GCI band")
    G["gci_max_pct_of_rise"] = float(m.group(1))
    m = _need(re.search(r"spatial invariance \*\*≤ ([0-9.]+) × band\*\*", text),
              "the spatial-invariance band")
    G["invariance_frac_of_band"] = float(m.group(1))
    m = _need(re.search(r"lumped\nvalidity \*\*\(T_max − T_min\)/\(T_mean − T_inf\) "
                        r"≤ ([0-9.]+)\*\*", text), "the lumped-validity band")
    G["lumped_max"] = float(m.group(1))
    m = _need(re.search(r"closure \*\*\|C − 1\| ≤ ([0-9.]+)\*\*", text),
              "the unplanted balance band")
    G["balance_abs_max"] = float(m.group(1))
    m = _need(re.search(r"planted balance response \*\*C_planted − C_unplanted ∈\n"
                        r"\[([0-9.]+), ([0-9.]+)\]\*\*", text), "the planted balance band")
    G["planted_lo"], G["planted_hi"] = float(m.group(1)), float(m.group(2))

    # -- section 6.4: the module-step row's band ----------------------------
    m = _need(re.search(r"analytic rise is `3\.0 × \(1 − e\^\{−0\.2\}\)` = "
                        r"\*\*([0-9.]+) K\*\*, so the 1 % band is\n\*\*([0-9.]+) mK\*\*", text),
              "the T20_LC_D band (section 6.4)")
    G["D_rise_K"] = float(m.group(1))
    G["D_band_mK_tabulated"] = float(m.group(2))
    G["D_band_K"] = G["band_frac_of_rise"] * G["D_rise_K"]
    if abs(1e3 * G["D_band_K"] - G["D_band_mK_tabulated"]) > 5e-4:
        refuse("T20_LC_D band cross-check failed: %.10g mK vs frozen %.10g mK"
               % (1e3 * G["D_band_K"], G["D_band_mK_tabulated"]))

    # -- section 7.1: the planted-zero control's registered clauses ---------
    m = _need(re.search(r"\*\*`PLANT = ([0-9.e+-]+) K`\*\*", text), "the registered PLANT")
    G["PLANT"] = float(m.group(1))
    m = _need(re.search(r"`floor > ([0-9.e+-]+) K`\*\*", text), "the registered floor ceiling")
    G["floor_max_K"] = float(m.group(1))
    m = _need(re.search(r"REFUSE if `seen\[PLANT\] < ([0-9.]+) × PLANT`", text),
              "the registered plant sizing clause")
    G["plant_sizing_frac"] = float(m.group(1))

    # -- section 9: the SEVEN registered cases ------------------------------
    # This is the structural defence against BOTH traps.  The case list comes from
    # the FROZEN TABLE -- never from what is on disk, never from the transcription
    # JSON -- so T20_LC_P10 cannot be dropped by being absent, and T20_LC_c cannot
    # acquire a row by being present.
    cases = {}
    for ln in text.splitlines():
        mm = re.match(r"^\| \*{0,2}`(T20_LC_[A-Za-z0-9]+)`\*{0,2} \|(.+)\|$", ln)
        if not mm:
            continue
        cols = [c.strip().replace("**", "").replace("`", "") for c in mm.group(2).split("|")]
        if len(cols) != 7:                      # the section 9 run-set table only
            continue
        cases[mm.group(1)] = dict(mesh=cols[0], cells=int(cols[1]), deltaT=float(cols[2]),
                                  endTime=float(cols[3]), steps=int(cols[4]),
                                  purpose=cols[5], graded=cols[6])
    if len(cases) != 7:
        refuse("the frozen run-set table (section 9) yielded %d cases, not the registered 7: %s"
               % (len(cases), sorted(cases)))

    # -- section 8: the registered ExecutionTime step counts, cross-checked --
    m = _need(re.search(r"Registered step counts for conjunct 5, all exact integers:\n(.+?)\n\n",
                        text, re.S), "the registered step counts (section 8)")
    blob = m.group(1)
    for c in cases:
        mm = re.search(r"`%s`[^0-9`]*\*\*([0-9]+)\*\*" % re.escape(c), blob)
        if mm and int(mm.group(1)) != cases[c]["steps"]:
            refuse("section 8 registers %s ExecutionTime lines for %s but section 9's table says "
                   "%d steps -- the frozen document disagrees with itself and this comparator "
                   "will not choose between them" % (mm.group(1), c, cases[c]["steps"]))

    # -- section 12: the verdict map's row ids ------------------------------
    row_ids = []
    for ln in text.splitlines():
        mm = re.match(r"^\| \*\*(V[0-9]|P[0-9]|R1–R6)\*\* \|", ln)
        if mm:
            tok = mm.group(1)
            row_ids.extend(["R%d" % i for i in range(1, 7)] if tok == "R1–R6" else [tok])
    if not row_ids:
        refuse("the frozen verdict map (section 12) yielded no row ids")
    _need(re.search(r"\| \*\*R1–R6\*\* \| the six predicted residuals of §4\.5 \| "
                    r"\*\*REPORTED beside the measured values, never gated\*\* \|", text),
          "the R1-R6 REPORTED-NEVER-GATED clause")

    # -- section 4.5: THE PREDICTIONS.  These are EXPECTATIONS, NOT GATES. ---
    m = _need(re.search(r"\| \*\*predicted net residual at τ\*\* \| \*\*([+−-][0-9.]+) mK\*\* "
                        r"\| \*\*([+−-][0-9.]+) mK\*\* \|", text), "the predicted residuals at tau")
    P["net_resid_mK"] = {("Q1", 1): _num(m.group(1)), ("Q2", 1): _num(m.group(2))}
    m = _need(re.search(r"\| \*\*predicted net residual at 3τ\*\* \| \*\*([+−-][0-9.]+) mK\*\* "
                        r"\| ([+−-][0-9.]+) mK \|", text), "the predicted residuals at 3 tau")
    P["net_resid_mK"][("Q1", 3)] = _num(m.group(1))
    P["net_resid_mK"][("Q2", 3)] = _num(m.group(2))
    m = _need(re.search(r"\| \*\*1\.5 s \(graded\)\*\* \| \*\*(−[0-9.]+) %\*\* \| "
                        r"(−[0-9.]+) % \| (−[0-9.]+) % \|", text),
              "the graded-level theta-error row (section 4.5)")
    P["theta_err_pct_graded"] = {1: _num(m.group(1)), 2: _num(m.group(2)), 3: _num(m.group(3))}
    m = _need(re.search(r"lumped model bias \| \*\*\+([0-9.]+) mK\*\* \| \*\*≈ 0\*\* \|", text),
              "the registered lumped model bias")
    P["lumped_bias_mK"] = float(m.group(1))
    # Section 4.5 says "these SIX predicted residuals" and TABULATES FOUR: the
    # Q1/Q2 pair at tau and the Q1/Q2 pair at 3 tau.  The 2 tau pair is the only
    # reading under which six exist, and it is DERIVED from the document's own
    # registered theta-error table and its own registered composition (net = Euler
    # lag + lumped bias).  Every R row prints which of the two it is.  NONE IS
    # GATED, so the choice creates no gate either way.
    lag2 = P["theta_err_pct_graded"][2] / 100.0 * G["rise_K"][2] * 1e3
    P["net_resid_mK"][("Q1", 2)] = lag2 + P["lumped_bias_mK"]
    P["net_resid_mK"][("Q2", 2)] = lag2

    # -- section 5.1: the predicted observed orders and GCIs ----------------
    P["p_predicted"], P["gci_predicted_pct"] = {}, {}
    for lbl, pp, gg in re.findall(r"^\| (τ|2τ|3τ) \| ([0-9.]+) \| ([0-9.]+) % \| "
                                  r"[0-9.]+ \| yes \|$", text, re.M):
        n = {"τ": 1, "2τ": 2, "3τ": 3}[lbl]
        P["p_predicted"][n] = float(pp)
        P["gci_predicted_pct"][n] = float(gg)

    # -- sections 5.2, 7.1, 7.2: the remaining registered EXPECTATIONS ------
    m = _need(re.search(r"\*\*prediction that they agree to < ([0-9.e+-]+) K\*\*", text),
              "the invariance prediction")
    P["invariance_predicted_K"] = float(m.group(1))
    m = _need(re.search(r"at 3τ ≤ [0-9.]+\*\*, predicted \*\*([0-9.e+-]+)\*\*", text),
              "the lumped-validity prediction")
    P["lumped_predicted"] = float(m.group(1))
    m = _need(re.search(r"Predicted \|C − 1\| < ([0-9.e+-]+)\.", text),
              "the balance-closure prediction")
    P["balance_predicted"] = float(m.group(1))
    m = _need(re.search(r"Predicted floor at `writePrecision 12`: \*\*≤ ([0-9.e+-]+) K\*\*", text),
              "the predicted detection floor")
    P["floor_predicted_K"] = float(m.group(1))

    return G, P, cases, row_ids, samples


PREREG_DIGEST = pin(PREREG_PATH, PREREG_SHA256, "T20_PREREGISTRATION.md")
_FROZEN_TEXT = open(PREREG_PATH, encoding="utf-8").read()
GATES, PREDICTIONS, FROZEN_CASES, FROZEN_ROW_IDS, SAMPLE_TIMES = parse_frozen(_FROZEN_TEXT)

if set(GATES) & set(PREDICTIONS):
    refuse("GATES and PREDICTIONS share the keys %s -- a gate and an expectation must never be "
           "the same object" % sorted(set(GATES) & set(PREDICTIONS)))

PREDICTION_PROVENANCE = {
    ("Q1", 1): "REGISTERED VERBATIM (section 4.5, 'predicted net residual at tau')",
    ("Q2", 1): "REGISTERED VERBATIM (section 4.5, 'predicted net residual at tau')",
    ("Q1", 3): "REGISTERED VERBATIM (section 4.5, 'predicted net residual at 3 tau')",
    ("Q2", 3): "REGISTERED VERBATIM (section 4.5, 'predicted net residual at 3 tau')",
    ("Q1", 2): "DERIVED FROM REGISTERED -- NOT TABULATED IN THE FROZEN DOCUMENT (section 4.5's "
               "theta-error table at 2 tau x section 1 line 4's rise, plus the registered "
               "lumped bias)",
    ("Q2", 2): "DERIVED FROM REGISTERED -- NOT TABULATED IN THE FROZEN DOCUMENT (section 4.5's "
               "theta-error table at 2 tau x section 1 line 4's rise)",
}

# R1..R6 <-> (reader, sample index).  See the note in parse_frozen.
R_ROWS = [("R1", "Q1", 1), ("R2", "Q1", 2), ("R3", "Q1", 3),
          ("R4", "Q2", 1), ("R5", "Q2", 2), ("R6", "Q2", 3)]
GATED_ROW_IDS = ["V1", "V2", "V3", "V4", "V5", "P1", "P2", "P3", "P4"]

SPATIAL_TRIPLE_REFERRAL = "OPEN"        # section 5.3.  NOT resolved here.

sys.path.insert(0, os.path.join(REPO, "scripts"))
from roache_triple import gci_equal, FS, STAGNANT_FLOOR, P_MIN        # noqa: E402

REGION = "cellRegion"
# Section 8 conjunct 4, VERBATIM: "The registered list for this rung is exactly
# {T}, and the check asserts presence of T, not absence of the others."  The
# thermal family's `T U p_rgh alphat nut k omega` DOES NOT APPLY -- there is no
# fluid region and those fields do not and must not exist.  Taken from T20's own
# frozen document and from the case's own settings, never by habit from another
# rung.  (The run tree does also carry `p`; conjunct 4 is a PRESENCE check on T
# and says nothing about p, so p's presence is neither required nor forbidden.)
FIELD_TUPLE = ("T",)
CONV_PATCHES = ("channelFaceLo", "channelFaceHi")
TRIPLE = ("T20_LC_c", "T20_LC_m", "T20_LC_f")       # section 5.1, r = 2 in TIME
SPATIAL = ("T20_LC_Sc", "T20_LC_f", "T20_LC_Sf")    # section 5.2, r = 2 in SPACE
REFINEMENT = 2.0


def load_registered(path=None):
    p = path or REG_PATH
    if not os.path.isfile(p):
        refuse("no T20_registered.json at %s" % p)
    if path is None:
        pin(p, REG_SHA256, "T20_registered.json")
    reg = json.load(open(p))
    if reg.get("prereg_commit") != PREREG_COMMIT:
        refuse("T20_registered.json cites freeze commit %r, not %r"
               % (reg.get("prereg_commit"), PREREG_COMMIT))
    # THE DOCUMENT WINS.  T20_registered.json says of itself: "if this file and
    # the document ever disagree, the document wins and THIS FILE is the thing
    # that is wrong."  So a disagreement REFUSES; it is never reconciled here.
    for c, jc in reg.get("cases", {}).items():
        if c not in FROZEN_CASES:
            refuse("T20_registered.json carries case %s which is NOT in the frozen section 9 "
                   "run-set table -- the document wins and the JSON is wrong" % c)
        f = FROZEN_CASES[c]
        for k in ("cells", "steps"):
            if int(jc[k]) != int(f[k]):
                refuse("T20_registered.json says %s.%s = %s, the frozen document says %s -- the "
                       "document wins and the JSON is wrong" % (c, k, jc[k], f[k]))
        for k in ("deltaT", "endTime"):
            if float(jc[k]) != float(f[k]):
                refuse("T20_registered.json says %s.%s = %s, the frozen document says %s -- the "
                       "document wins and the JSON is wrong" % (c, k, jc[k], f[k]))
    return reg


REG = load_registered()
PH = REG["physics"]


# ---------------------------------------------------------------------------
# THE EXACT SOLUTION -- section 1 line 2: "derived in this document (section 3)
# and RE-DERIVED INDEPENDENTLY IN THE COMPARATOR, never transcribed from a page."
# The re-derivation is then CROSS-CHECKED against the frozen band table's rise
# column, which validates the physics block, the geometry and the arithmetic in
# one step.  A disagreement is a REFUSAL.
# ---------------------------------------------------------------------------
V_BODY = PH["Lx"] * PH["Ly"] * PH["Lz"]                  # m3 per registered depth
A_CONV = 2.0 * PH["Lx"] * PH["Lz"]                       # both 100 mm faces convect
L_C = V_BODY / A_CONV
TAU = PH["rho"] * PH["cp"] * L_C / PH["h_conv"]
DT_SS = PH["q_volumetric"] * L_C / PH["h_conv"]


def exact_T(t):
    """T(t) = T_inf + (q''' V/(h A))(1 - exp(-t/tau)),  tau = rho cp V/(h A)."""
    return PH["T_inf"] + DT_SS * (1.0 - math.exp(-t / TAU))


for _n in (1, 2, 3):
    _r = exact_T(_n * TAU) - PH["T_inf"]
    if abs(_r - GATES["rise_K"][_n]) > 5e-9:
        refuse("the comparator's INDEPENDENTLY RE-DERIVED analytic rise at %d tau is %.12g K but "
               "the frozen table registers %.12g K -- section 1 line 2 requires the re-derivation "
               "and it does not reproduce" % (_n, _r, GATES["rise_K"][_n]))
if abs(TAU - PH["derived_tau_s"]) > 1e-9 or abs(DT_SS - PH["derived_dT_steady_K"]) > 1e-12:
    refuse("the re-derived tau = %.12g s / dT_ss = %.12g K do not reproduce the frozen section 4.3 "
           "values %.12g / %.12g" % (TAU, DT_SS, PH["derived_tau_s"], PH["derived_dT_steady_K"]))
if abs((exact_T(FROZEN_CASES["T20_LC_D"]["endTime"]) - PH["T_inf"]) - GATES["D_rise_K"]) > 5e-7:
    refuse("the re-derived rise at the T20_LC_D sample does not reproduce the frozen section 6.4 "
           "value %.10g K" % GATES["D_rise_K"])


# ---------------------------------------------------------------------------
# THE READERS
# ---------------------------------------------------------------------------
def _field_path(case_dir, time, name):
    return os.path.join(case_dir, str(time), REGION, name)


def read_internal(case_dir, time, name, ncells):
    """FLAT list of ncells values.  Handles `uniform X` and `nonuniform
    List<scalar> N ( ... )`.  Refuses on a length mismatch, which is also how the
    uniform-mesh assumption behind Q1's volume weighting is enforced."""
    p = _field_path(case_dir, time, name)
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    m = re.search(r"internalField\s+uniform\s+([0-9eE.+-]+)\s*;", txt)
    if m:
        return [float(m.group(1))] * ncells
    m = re.search(r"internalField\s+nonuniform[^(]*\(\s*(.*?)\n\)", txt, re.S)
    if not m:
        return None
    vals = [float(v) for v in m.group(1).split()]
    if len(vals) != ncells:
        refuse("%s holds %d internal values, the frozen mesh registers %d" % (p, len(vals), ncells))
    return vals


def _patch_spans(txt):
    """Structural walk of boundaryField -> [(key, body_start, body_end)].  A block
    key is either a bare patch name or a QUOTED REGEX (`"channelFaceLo|
    channelFaceHi"`, which is how the INITIAL field is written), and both
    spellings must be understood or the t = 0 read silently finds nothing.
    Offsets are returned so a planter can splice without a text search that would
    hit two identical patch bodies at once."""
    i = txt.find("boundaryField")
    if i < 0:
        return []
    j = txt.find("{", i)
    if j < 0:
        return []
    out, k, depth = [], j + 1, 1
    key, buf, kstart = None, [], None
    while k < len(txt) and depth >= 1:
        ch = txt[k]
        if ch == "{":
            if depth == 1:
                key = "".join(buf).strip()
                buf, kstart = [], k + 1
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 1 and key is not None:
                out.append((key, kstart, k))
                key, buf = None, []
            elif depth == 0:
                break
        elif depth == 1:
            buf.append(ch)
        k += 1
    return out


def _key_matches(key, patch):
    k = key.strip()
    if k == patch:
        return True
    if len(k) > 1 and k[0] == '"' and k[-1] == '"':
        try:
            return bool(re.fullmatch(k[1:-1], patch))
        except re.error:
            return False
    return False


def read_patch(case_dir, time, name, patch, nfaces):
    """The patch's `value` entry -- NEVER `refValue`, which on this mixed BC is
    the ambient 293 and would read as a perfect answer for entirely the wrong
    reason."""
    p = _field_path(case_dir, time, name)
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    for key, a, b in _patch_spans(txt):
        if not _key_matches(key, patch):
            continue
        body = txt[a:b]
        m = re.search(r"^\s*value\s+uniform\s+([0-9eE.+-]+)\s*;", body, re.M)
        if m:
            return [float(m.group(1))] * nfaces
        m = re.search(r"^\s*value\s+nonuniform[^(]*\(\s*(.*?)\n\)", body, re.M | re.S)
        if not m:
            return None
        vals = [float(v) for v in m.group(1).split()]
        if len(vals) != nfaces:
            refuse("%s patch %s holds %d face values, the frozen mesh registers %d"
                   % (p, patch, len(vals), nfaces))
        return vals
    return None


def Q1_mean(case_dir, time, nx, ny):
    """Q1 -- VOLUME-MEAN temperature of the solid region.  Section 6.3 registers
    ONE BLOCK WITH UNIFORM GRADING and one cell in z, so every cell volume is
    Lx*Ly*Lz/(nx*ny) identically and the volume-weighted mean IS the arithmetic
    mean.  The cell count is not assumed: read_internal REFUSES unless the field
    holds exactly nx*ny values."""
    v = read_internal(case_dir, time, "T", nx * ny)
    return None if v is None else sum(v) / len(v)


def Q2_mean(case_dir, time, nx):
    """Q2 -- AREA-MEAN temperature over the two convecting patches.  Each patch
    carries nx faces of area (Lx/nx)*Lz, identical, so the area-weighted mean is
    the arithmetic mean over the 2*nx face values."""
    acc = []
    for pt in CONV_PATCHES:
        v = read_patch(case_dir, time, "T", pt, nx)
        if v is None:
            return None
        acc.extend(v)
    return sum(acc) / len(acc)


def written_times(case_dir):
    """Every written time directory name, ascending.  Names carry float drift under
    a non-integer deltaT -- T20_LC_D's endTime directory is literally
    `299.99999999987216` -- so the NAME is kept as the read key and the FLOAT is
    used only for arithmetic and ordering."""
    if not os.path.isdir(case_dir):
        return []
    ts = [t for t in os.listdir(case_dir) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t)]
    return sorted(ts, key=float)


def _sig12(x):
    """Section 8 conjunct 3: 'compared as a float with timePrecision 12'.  The
    registered timePrecision is 12 SIGNIFICANT FIGURES (section 6.2), which is
    exactly the representation OpenFOAM used to WRITE the directory name, so the
    comparison is made in the representation the name was produced in.  This is
    the frozen instruction, not a tolerance chosen here."""
    return float("%.12g" % x)


def _time_key(case_dir, t):
    for name in written_times(case_dir):
        if _sig12(float(name)) == _sig12(t):
            return name
    return None


# ---------------------------------------------------------------------------
# RULE 3 -- THE PLANTED-ZERO CONTROL.  Section 7.1's nine registered clauses.
# ---------------------------------------------------------------------------
PLANT = GATES["PLANT"]
PLANT_LADDER = (1.0, 1e-1, 1e-2, PLANT, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9)


def write_precision(case_dir):
    """The case's OWN `writePrecision`, read from its OWN system/controlDict.

    A plant must be written back at the precision the SOLVER would have written
    it at, or the control silently measures the PLANTER's precision instead of the
    FIELD's -- and section 10 S5, whose whole subject is a field written at a
    coarse precision, would be untestable.

    IT IS READ, NOT INFERRED.  An earlier draft of this file inferred the
    precision by counting significant digits in the written tokens, and that is
    WRONG in a way that quietly loosens the instrument: `%g` STRIPS TRAILING
    ZEROS, so a field written at 6 significant figures whose value is 295.850
    appears in the file as `295.85` and infers as 5 -- a TEN-FOLD understatement
    of the field's real resolution, in the direction that makes the reader look
    blinder than it is.  The setting is a case fact and is available; guessing it
    from the bytes is not.  REFUSES rather than degrades."""
    p = os.path.join(case_dir, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("planted-zero control: no system/controlDict under %s, so the case's own "
               "writePrecision cannot be read and the plant cannot be written back at the "
               "precision the solver would have used" % case_dir)
    m = re.search(r"^\s*writePrecision\s+([0-9]+)\s*;", open(p).read(), re.M)
    if not m:
        refuse("planted-zero control: %s carries no writePrecision entry" % p)
    n = int(m.group(1))
    if not 1 <= n <= 17:
        refuse("planted-zero control: %s registers writePrecision %d, outside 1..17" % (p, n))
    return n


def _plant_internal(path, mag, prec):
    """Clause 6: for Q1 the plant goes into EVERY INTERNAL CELL, so the expected
    shift of a volume mean is exactly PLANT and clause 5 tests the READER rather
    than 1/ncells.  Planted BY LINE INDEX off the structurally located
    internalField list, written back at the CASE'S OWN writePrecision."""
    lines = open(path).read().splitlines(True)
    start = None
    for i, ln in enumerate(lines):
        if "internalField" in ln and "nonuniform" in ln:
            for j in range(i, min(i + 5, len(lines))):
                if lines[j].strip() == "(":
                    start = j + 1
                    break
            break
    if start is None:
        refuse("planted-zero control: could not locate the internalField list STRUCTURALLY in %s "
               "(a `uniform` internalField cannot be planted by line index)" % path)
    end = start
    while end < len(lines) and lines[end].strip() not in (")", ");"):
        end += 1
    fmt = "%%.%dg\n" % prec
    n = 0
    for k in range(start, end):
        s = lines[k].strip()
        if not s:
            continue
        lines[k] = fmt % (float(s) + mag)
        n += 1
    open(path, "w").write("".join(lines))
    return n


def _plant_patch(path, mag, prec):
    """Clause 6: for Q2 the plant goes into EVERY FACE VALUE of BOTH convecting
    patches.  Where a patch writes `value uniform X`, that single entry IS every
    face value; the number of VALUES WRITTEN is what is recorded, and the output
    also names how many faces they cover."""
    txt = open(path).read()
    spans = [(k, a, b) for k, a, b in _patch_spans(txt)
             if any(_key_matches(k, p) for p in CONV_PATCHES)]
    if not spans:
        refuse("planted-zero control: no boundaryField block matches the convecting patches %s "
               "in %s" % (list(CONV_PATCHES), path))
    n = 0
    for key, a, b in reversed(spans):                   # splice from the end
        body = txt[a:b]
        fmt = "%%.%dg" % prec
        m = re.search(r"^(\s*value\s+uniform\s+)([0-9eE.+-]+)(\s*;)", body, re.M)
        if m:
            nb = body[:m.start()] + m.group(1) + (fmt % (float(m.group(2)) + mag)) + \
                m.group(3) + body[m.end():]
            n += 1
        else:
            m = re.search(r"^(\s*value\s+nonuniform[^(]*\(\s*)(.*?)(\n\))", body, re.M | re.S)
            if not m:
                refuse("planted-zero control: patch block %r in %s carries no `value` entry"
                       % (key, path))
            vals = m.group(2).split()
            nb = body[:m.start()] + m.group(1) + \
                "\n".join(fmt % (float(v) + mag) for v in vals) + m.group(3) + body[m.end():]
            n += len(vals)
        txt = txt[:a] + nb + txt[b:]
    open(path, "w").write(txt)
    return n


def planted_zero_control(case_dir, time, nx, ny):
    """Section 7.1's nine clauses, in the registered order.  REFUSES (exit 2)
    rather than degrades.  The ONLY tolerance anywhere in this control is RELATIVE
    (clause 5, `seen[PLANT] < 0.1 x PLANT`); the negative arm's threshold is
    EXACTLY ZERO and the floor comparison is `d > 0.0` with no epsilon.

    T3's `seen >= PLANT - 1e-15` is NOT adopted and section 7.1 says why: on a
    ~300 K field that slack sits far below one ULP, so the outcome turns on the
    sign of a rounding wiggle."""
    tmp = tempfile.mkdtemp(prefix="t20pz_")
    try:
        dst = os.path.join(tmp, os.path.basename(case_dir))
        shutil.copytree(case_dir, dst, symlinks=True)                       # clause 1
        if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
            refuse("planted-zero control clause 1: the scratch copy resolved INSIDE the case tree")
        prec = write_precision(dst)
        readers = (("Q1", lambda d: Q1_mean(d, time, nx, ny), _plant_internal, nx * ny),
                   ("Q2", lambda d: Q2_mean(d, time, nx), _plant_patch, 2 * nx))
        p = _field_path(dst, time, "T")
        out = {}
        for name, fn, planter, ncover in readers:
            base = fn(dst)
            if base is None:
                refuse("planted-zero control %s: the reader returned nothing on the UNPLANTED "
                       "copy -- there is nothing to plant into" % name)
            again = fn(dst)                                                 # clause 2
            dneg = abs(base - again)
            if dneg != 0.0:
                refuse("planted-zero control %s NEGATIVE ARM FAILED: %.17g on IDENTICAL BYTES -- "
                       "the reader is NOISY" % (name, dneg))
            orig = open(p).read()
            seen, floor, nplanted = {}, None, 0
            try:
                for mag in PLANT_LADDER:                                    # clause 3
                    open(p, "w").write(orig)
                    nplanted = planter(p, mag, prec)
                    got = fn(dst)
                    if got is None:
                        refuse("planted-zero control %s: the reader returned nothing at plant %.3g"
                               % (name, mag))
                    d = abs(got - base)
                    seen[mag] = d
                    if d > 0.0:                                             # exact, no epsilon
                        floor = mag
            finally:
                open(p, "w").write(orig)                                    # clause 9
            if floor is None:                                               # clause 4
                refuse("planted-zero control %s POSITIVE ARM FAILED: no plant magnitude in %s was "
                       "visible -- the reader is BLIND" % (name, list(PLANT_LADDER)))
            if seen[PLANT] < GATES["plant_sizing_frac"] * PLANT:            # clause 5
                # `floor` is formatted with %s, not %.3g: clause 4 has already
                # refused when it is None, but a message that CRASHES on the
                # unreachable branch turns a refusal into a traceback the moment
                # clause 4 is ever weakened, and a comparator must be able to say
                # why it is stopping under every mutation of itself.
                refuse("planted-zero control %s CLAUSE 5: the REGISTERED plant %.6g moved the read "
                       "by only %.6g, below the registered %g x PLANT, while %s WAS visible -- "
                       "the reader cannot see a perturbation of the registered size"
                       % (name, PLANT, seen[PLANT], GATES["plant_sizing_frac"], floor))
            if floor > GATES["floor_max_K"]:                                # clause 8
                refuse("planted-zero control %s CLAUSE 8: the DEMONSTRATED DETECTION FLOOR %.3g K "
                       "is coarser than the registered ceiling %.3g K (one hundredth of the "
                       "tightest band) -- an instrument whose demonstrated resolution is not at "
                       "least 100x finer than the band it decides has no business deciding it"
                       % (name, floor, GATES["floor_max_K"]))
            ratio = seen[PLANT] / PLANT
            out[name] = dict(status="PASS", plant=PLANT, values_planted=nplanted,
                             case_writePrecision=prec,
                             faces_or_cells_covered=ncover, recovered=seen[PLANT],
                             recovery_ratio=ratio,
                             tight_relative_predicate_REPORTED_NOT_GATED=bool(
                                 seen[PLANT] >= PLANT * (1.0 - 1e-9)),
                             negative_arm=dneg, demonstrated_detection_floor=floor,
                             registered_floor_ceiling=GATES["floor_max_K"],
                             ladder={("%g" % k): v for k, v in seen.items()})
            print("  planted-zero %-3s PASS: plant %.6g into %d value(s) covering %d %s, read "
                  "moved %.6g (ratio %.9f), negative arm %.17g, floor %.1g <= ceiling %.1g"
                  % (name, PLANT, nplanted, ncover, "cells" if name == "Q1" else "faces",
                     seen[PLANT], ratio, dneg, floor, GATES["floor_max_K"]))
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# RULE 4 -- STRICT COMPLETION, section 8's six conjuncts.  ALL-OR-NOTHING.
# ---------------------------------------------------------------------------
def status_of(root, case):
    p = os.path.join(root, "STATUS.%s" % case)
    if not os.path.isfile(p):
        return None
    return dict(re.findall(r"^([A-Za-z_0-9]+)=(.*)$", open(p).read(), re.M))


def completion(root, case, frozen):
    """Returns (ok, [failed conjunct descriptions], detail).  A run is done only if
    ALL of it holds."""
    d = os.path.join(root, case)
    bad, det = [], dict(case=case)
    if not os.path.isdir(d):
        return False, ["the case directory does not exist -- the case was NEVER BUILT OR RUN"], det
    st = status_of(root, case)
    if st is None:                                                          # conjunct 1
        bad.append("conjunct 1: no STATUS.%s, so rc is unknown" % case)
    else:
        det.update(rc=st.get("rc"), wall_s=st.get("wall_s"), note=st.get("note"))
        if st.get("rc") != "0":
            bad.append("conjunct 1: rc = %r, not 0" % st.get("rc"))
    log = os.path.join(d, "log.solve")                                      # conjunct 2
    if not os.path.isfile(log):
        bad.append("conjunct 2: no log.solve")
        body = ""
    else:
        body = open(log, errors="replace").read()
        n_end = len(re.findall(r"^End\s*$", body, re.M))
        det["End_lines"] = n_end
        if n_end != 1:
            bad.append("conjunct 2: %d End lines, registered 1" % n_end)
    ts = [t for t in written_times(d) if float(t) > 0]                      # conjunct 3
    if not ts:
        bad.append("conjunct 3: no time directory above 0")
        last = None
    else:
        last = ts[-1]
        det.update(last_time_dir=last, endTime_registered=frozen["endTime"])
        if _sig12(float(last)) != _sig12(frozen["endTime"]):
            bad.append("conjunct 3: greatest time directory %r != registered endTime %g at "
                       "timePrecision 12" % (last, frozen["endTime"]))
        elif last != ("%g" % frozen["endTime"]):
            det["time_dir_float_drift"] = (
                "the directory NAME is %r, not %g; it compares equal only at the registered "
                "timePrecision 12 (section 8 conjunct 3).  REPORTED, not absorbed."
                % (last, frozen["endTime"]))
    if last is not None:                                                    # conjunct 4
        det["fields_required"] = list(FIELD_TUPLE)
        missing = [f for f in FIELD_TUPLE if not os.path.isfile(_field_path(d, last, f))]
        if missing:
            bad.append("conjunct 4: missing %s in %s/%s/" % (missing, last, REGION))
    n_ex = len(re.findall(r"ExecutionTime", body))                          # conjunct 5
    det.update(ExecutionTime_lines=n_ex, steps_registered=frozen["steps"])
    if n_ex != frozen["steps"]:
        bad.append("conjunct 5: %d ExecutionTime lines, registered %d" % (n_ex, frozen["steps"]))
    zero = _field_path(d, "0", "T")                                         # conjunct 6
    if not os.path.isfile(zero):
        bad.append("conjunct 6: no 0/%s/T, so the AGE GUARD has no datum" % REGION)
    elif last is not None:
        t0 = os.stat(zero).st_mtime
        det["mtime_0_T"] = t0
        for f in FIELD_TUPLE:
            fp = _field_path(d, last, f)
            if os.path.isfile(fp):
                tf = os.stat(fp).st_mtime
                det["mtime_end_%s" % f] = tf
                if not tf > t0:
                    bad.append("conjunct 6 (AGE GUARD): %s/%s/%s is NOT NEWER than 0/%s/T "
                               "(%.6f <= %.6f) -- the field does not date to the run that was "
                               "allowed to produce it" % (last, REGION, f, REGION, tf, t0))
    return (not bad), bad, det


# ---------------------------------------------------------------------------
# RULE 5 -- THE GATE.  apply_gate() is the ONLY function that writes a verdict.
# ---------------------------------------------------------------------------
def triple_of(vals, r, dim):
    """MEASURED DEFECT IN A SHARED INSTRUMENT, GUARDED HERE AND REPORTED UPWARD --
    NOT REPAIRED, because scripts/roache_triple.py belongs to another team and is
    under the standing plumbing freeze.

    `gci_equal` raises an UNCAUGHT `ValueError: math domain error` at
    roache_triple.py:261 whenever `e32 == 0.0` and `e21 != 0.0` -- the two coarser
    levels identical and the finest different -- because it takes `log(abs(e32 /
    e21))` without guarding a zero numerator.  It guards `e21 == 0` (EXACT) and
    the sign (OSCILLATORY) but not this case, so a legitimate ladder crashes the
    comparator instead of being classified.  T20 reaches it on its own SPATIAL
    triple whenever the two coarser meshes agree and the finest does not, which is
    precisely the shape section 5.2 expects a spatial ladder here to have.

    Caught and mapped to `NO_ORDER`, which roache_triple.py's own
    NOT_A_RESULT_STATES already lists.  A state that is not CONVERGING is NOT A
    RESULT under rule 5, so the guard is CONSERVATIVE: it can only make a row
    worse and can never manufacture a pass."""
    try:
        return gci_equal(vals[0], vals[1], vals[2], r, dim, fs=FS)
    except (ValueError, ZeroDivisionError) as e:
        return dict(state="NO_ORDER", dim=dim, r21=r, r32=r,
                    e21=vals[1] - vals[2], e32=vals[0] - vals[1], fs=FS, form="equal",
                    refused_because="roache_triple.gci_equal raised %s: %s -- the fitted order "
                                    "does not exist for this triple" % (type(e).__name__, e))


def fmt_tr(tr):
    if not tr:
        return "n/a"
    p, g = tr.get("order"), tr.get("GCI_pct")
    return "%s p=%s GCI_abs=%s" % (
        tr["state"], ("%.4f" % p) if p is not None else "n/a",
        ("%.4e K" % tr["GCI_abs"]) if g is not None else "REFUSED (non-monotone)")


def apply_gate(value, lo, hi, tr, gate1_ok, gate1_why, extra_nar=()):
    """Rule 5's fixed order, ONE WAY.  `value` is ALWAYS the FINE value; the
    Richardson extrapolate is never passed in.  The band verdict is computed FIRST
    and unconditionally and is returned beside the final verdict, so the gate can
    be SEEN to have only ever turned a PASS or GATE FAIL INTO a NOT A RESULT.

    `tr` may be None for a registered SINGLE-LEVEL row (section 12 V3: 'no triple;
    single level, stated'), in which case clause (2) is skipped BY REGISTRATION and
    the row records that it was."""
    bv = "PASS" if lo <= value <= hi else "GATE FAIL"
    if not gate1_ok:
        return "NOT A RESULT", bv, "gate (1): " + gate1_why
    for why in extra_nar:
        if why:
            return "NOT A RESULT", bv, why
    if tr is not None and tr["state"] != "CONVERGING":
        p = tr.get("order")
        return ("NOT A RESULT", bv,
                "gate (2): the temporal triple is %s%s -- rule 5 makes a triple that is not "
                "CONVERGING NOT A RESULT whatever its value says (STAGNANT_FLOOR=%g, P_MIN=%g, "
                "Fs=%g)" % (tr["state"], (" (p = %.4g)" % p) if p is not None else "",
                            STAGNANT_FLOOR, P_MIN, FS))
    return bv, bv, ""


# ---------------------------------------------------------------------------
# Q3 -- the cumulative energy-balance instrument (section 7.2)
# ---------------------------------------------------------------------------
def balance_C(case_dir, nx, ny):
    """C(t) = (E_stored + E_conv)/E_src at endTime.

    E_src uses the REGISTERED q''', NEVER the value in the case's own fvOptions.
    That is what makes the planted arm visible: the instrument cannot compensate
    for a source it is not told about, and the unplanted C ~ 1 is therefore a
    MEASUREMENT and not a reader returning unity by construction."""
    ts = written_times(case_dir)
    if len(ts) < 2:
        return None, "fewer than two written times"
    T0 = Q1_mean(case_dir, ts[0], nx, ny)
    if T0 is None:
        return None, "no readable T at t = %s" % ts[0]
    e_conv, prev_t, prev_f, Tm_end = 0.0, None, None, None
    for t in ts:
        Tm = Q1_mean(case_dir, t, nx, ny)
        Ts = Q2_mean(case_dir, t, nx)
        if Tm is None or Ts is None:
            return None, "unreadable T at t = %s" % t
        f = PH["h_conv"] * A_CONV * (Ts - PH["T_inf"])
        if prev_t is not None:
            e_conv += 0.5 * (f + prev_f) * (float(t) - prev_t)
        prev_t, prev_f, Tm_end = float(t), f, Tm
    t_end = float(ts[-1])
    e_src = PH["q_volumetric"] * V_BODY * t_end
    if e_src == 0.0:
        return None, "E_src is zero"
    e_stored = PH["rho"] * PH["cp"] * V_BODY * (Tm_end - T0)
    return dict(C=(e_stored + e_conv) / e_src, E_src=e_src, E_stored=e_stored,
                E_conv=e_conv, t_end=t_end, n_written=len(ts)), ""


def _mesh(case):
    c = REG["cases"].get(case)
    if c:
        return int(c["nx"]), int(c["ny"])
    # T20_LC_P10 is absent from the transcription BY REGISTRATION (its builder
    # cannot honour it).  Its mesh is the frozen BASE mesh; taken from the frozen
    # cell count, matched against a case whose mesh IS transcribed.
    n = FROZEN_CASES[case]["cells"]
    for cc in REG["cases"].values():
        if int(cc["cells"]) == n:
            return int(cc["nx"]), int(cc["ny"])
    refuse("no registered mesh for %s" % case)


# ---------------------------------------------------------------------------
# THE GRADE
# ---------------------------------------------------------------------------
def grade(root, json_out, quiet=False):
    res = dict(rung="T20", prereg=os.path.relpath(PREREG_PATH, REPO),
               prereg_commit=PREREG_COMMIT, prereg_sha256=PREREG_DIGEST,
               analyst_blind=False,
               non_blind_disclosure=(
                   "T20's gated grading is NO LONGER ANALYST-BLIND: the pre-registered "
                   "predictions of sections 4.5 and 5.1 were read before this comparator was "
                   "written.  The bands were frozen at %s BEFORE that, so CLAUDE.md rule 2's "
                   "evidentiary content survives intact." % PREREG_COMMIT[:8]),
               spatial_triple_referral=SPATIAL_TRIPLE_REFERRAL,
               registered_field_tuple=list(FIELD_TUPLE),
               rows_not_in_the_verdict_map=(
                   "T20_LC_c and T20_LC_m completed and are graded 'triple only' (section 9).  "
                   "They are the coarse and medium levels of V1/V2's temporal triple and carry "
                   "NO verdict of their own.  Six cases running does not make six graded rows."),
               rows=[], reported_rows=[], planted_zero_controls={})

    # ---- section 7 criterion (i): STRICT COMPLETION, ALL SEVEN CASES -------
    print("-- section 7 criterion (i): strict completion (section 8), all %d REGISTERED cases "
          "(section 9) --" % len(FROZEN_CASES))
    comp, fails = {}, []
    for case in sorted(FROZEN_CASES):
        ok, bad, det = completion(root, case, FROZEN_CASES[case])
        comp[case] = dict(complete=ok, failures=bad, detail=det)
        print("  [%s] %-14s %s" % ("ok  " if ok else "FAIL", case,
                                   "all six conjuncts hold" if ok else bad[0]))
        for extra in bad[1:]:
            print("       %s" % extra)
        if det.get("time_dir_float_drift"):
            print("       NOTE: %s" % det["time_dir_float_drift"])
        if not ok:
            fails.append(case)
    res["completion"] = comp
    if fails:
        m = re.search(r"\| \*\*V5\*\* \| Q3 balance, planted \+10 %, `(T20_LC_[A-Za-z0-9]+)`",
                      _FROZEN_TEXT)
        v5_case = m.group(1) if m else None
        msg = ["Registered cases failing strict completion: %s." % ", ".join(fails)]
        if v5_case in fails:
            msg += ["",
                    "THIS INCLUDES %s, WHICH IS V5's ONLY CASE." % v5_case,
                    "Section 12 V5: 'a refusal here makes the WHOLE RUNG NOT A RESULT'.",
                    "Section 7.2: 'an instrument that cannot see a planted 10 % is not entitled",
                    "to certify a 1 % agreement'.  The planted arm is what proves the unplanted",
                    "C ~ 1 is a MEASUREMENT and not a reader returning unity by construction.",
                    "Without it V4 is an unwitnessed number, and V1/V2/V3 rest on an instrument",
                    "never shown able to see a 10 % error."]
        msg += ["",
                "Section 7 criterion (i): 'any case failing any conjunct gets no marker and the",
                "whole rung is NOT A RESULT, the comparator refusing to grade a partial rung'.",
                "There is no flag that bypasses this."]
        not_a_result("\n".join(msg))

    # ---- section 7 criterion (ii): INSTRUMENT ADMISSION --------------------
    print("-- section 7 criterion (ii): instrument admission (rule 3, section 7.1) --")
    nx_f, ny_f = _mesh("T20_LC_f")
    df = os.path.join(root, "T20_LC_f")
    key3 = _time_key(df, SAMPLE_TIMES[2])
    if key3 is None:
        refuse("T20_LC_f has no written time equal to %g at timePrecision 12" % SAMPLE_TIMES[2])
    res["planted_zero_controls"]["T20_LC_f"] = planted_zero_control(df, key3, nx_f, ny_f)

    def q_at(case, t):
        nx, ny = _mesh(case)
        d = os.path.join(root, case)
        key = _time_key(d, t)
        if key is None:
            refuse("no written time equal to %g (at timePrecision 12) in %s" % (t, case))
        return Q1_mean(d, key, nx, ny), Q2_mean(d, key, nx)

    # ---- the TEMPORAL triple (rule 5) and the SPATIAL triple (section 5.3) -
    temporal, spatial = {}, {}
    for i, t in enumerate(SAMPLE_TIMES, start=1):
        temporal[("Q1", i)] = triple_of([q_at(c, t)[0] for c in TRIPLE], REFINEMENT, 1)
        temporal[("Q2", i)] = triple_of([q_at(c, t)[1] for c in TRIPLE], REFINEMENT, 1)
    t3 = SAMPLE_TIMES[2]
    spatial["Q1"] = triple_of([q_at(c, t3)[0] for c in SPATIAL], REFINEMENT, 2)
    spatial["Q2"] = triple_of([q_at(c, t3)[1] for c in SPATIAL], REFINEMENT, 2)
    res["spatial_triple"] = {k: {a: b for a, b in v.items() if a != "values"}
                             for k, v in spatial.items()}
    print("-- section 5.3: the SPATIAL triple is COMPUTED, CLASSIFIED and REPORTED, and GATED ON "
          "NOWHERE.  The section 5.3 referral to verification is %s. --" % SPATIAL_TRIPLE_REFERRAL)
    for k in ("Q1", "Q2"):
        print("  spatial %s (Sc/f/Sf, r=2, dim=2): %s" % (k, fmt_tr(spatial[k])))
    print("  Section 5.2 pre-registers EXACT here, for PHYSICS and not for a defect.  If")
    print("  verification rules that an EXACT spatial triple forces the rows to NOT A RESULT,")
    print("  section 5.3 accepts that outcome without appeal and every row below moves ONE WAY.")

    # ---- P2: spatial invariance (ONE-WAY: failure => V1/V2/V3 NOT A RESULT) -
    inv_band = GATES["invariance_frac_of_band"] * GATES["band_K"][3]
    inv, inv_worst = {}, 0.0
    for c in ("T20_LC_Sc", "T20_LC_Sf"):
        for q, idx in (("Q1", 0), ("Q2", 1)):
            dd = abs(q_at(c, t3)[idx] - q_at("T20_LC_f", t3)[idx])
            inv["%s:%s" % (c, q)] = dd
            inv_worst = max(inv_worst, dd)
    p2_ok = inv_worst <= inv_band
    res["reported_rows"].append(dict(
        row="P2", kind="GATE", quantity="spatial invariance, Sc/Sf vs f at 3 tau",
        measured_K=inv_worst, band_K=inv_band, verdict="PASS" if p2_ok else "GATE FAIL",
        per_case=inv))
    p2_nar = ("" if p2_ok else
              "P2 (spatial invariance) FAILED at %.4g K against %.4g K: section 5.2 registers "
              "ONE-WAY that a failure means the body is NOT LUMPED, so the lumped REFERENT's "
              "validity assumption is violated and Q1/Q2/Q3 become NOT A RESULT -- not GATE FAIL, "
              "and no threshold may be moved to rescue the row" % (inv_worst, inv_band))

    # ---- V1, V2 -----------------------------------------------------------
    for q, rowid in (("Q1", "V1"), ("Q2", "V2")):
        for i, t in enumerate(SAMPLE_TIMES, start=1):
            vals = [q_at(c, t)[0 if q == "Q1" else 1] for c in TRIPLE]
            val, ex, band = vals[2], exact_T(t), GATES["band_K"][i]
            tr = temporal[(q, i)]
            gci_rise = (100.0 * tr["GCI_abs"] / GATES["rise_K"][i]
                        if tr.get("GCI_pct") is not None else None)
            extra = [p2_nar]
            # Section 1 line 4 freezes p in [p_lo, p_hi] and GCI_fine < x % OF THE
            # RISE as BANDS, but section 12 gives them no row.  They are therefore
            # applied ONE WAY inside the temporal-triple step: they may turn a row
            # INTO NOT A RESULT and may never rescue one.  Recorded as an ambiguity
            # in the frozen document, resolved in the only direction that cannot
            # manufacture a pass.
            if tr["state"] == "CONVERGING":
                if not (GATES["p_lo"] <= tr["order"] <= GATES["p_hi"]):
                    extra.append("registered band (section 1 line 4): the observed order %.4f is "
                                 "outside p in [%g, %g]"
                                 % (tr["order"], GATES["p_lo"], GATES["p_hi"]))
                if gci_rise is not None and gci_rise >= GATES["gci_max_pct_of_rise"]:
                    extra.append("registered band (section 1 line 4): GCI_fine %.4f %% of the rise "
                                 "is not < %g %%" % (gci_rise, GATES["gci_max_pct_of_rise"]))
            v, bv, note = apply_gate(val, ex - band, ex + band, tr, True, "", extra)
            res["rows"].append(dict(
                row=rowid, quantity=q, sample="%d tau" % i, t_s=t, case="T20_LC_f",
                measured_K=val, reference_K=ex, deviation_K=val - ex,
                deviation_mK=1e3 * (val - ex), band_K=band, band_mK=1e3 * band,
                verdict=v, band_verdict=bv, note=note,
                temporal_triple={a: b for a, b in tr.items() if a != "values"},
                temporal_triple_values=vals,
                spatial_triple={a: b for a, b in spatial[q].items() if a != "values"},
                GCI_pct_of_rise=gci_rise))

    # ---- V3: Q2 at 300 s on T20_LC_D.  NO TRIPLE; single level, STATED. ----
    tD = FROZEN_CASES["T20_LC_D"]["endTime"]
    nxD, nyD = _mesh("T20_LC_D")
    dD = os.path.join(root, "T20_LC_D")
    keyD = _time_key(dD, tD)
    q2D, q1D = Q2_mean(dD, keyD, nxD), Q1_mean(dD, keyD, nxD, nyD)
    exD, bandD = exact_T(tD), GATES["D_band_K"]
    vD, bvD, noteD = apply_gate(q2D, exD - bandD, exD + bandD, None, True, "", [p2_nar])
    res["rows"].append(dict(
        row="V3", quantity="Q2", sample="t = %g s (module step)" % tD, t_s=tD, case="T20_LC_D",
        measured_K=q2D, reference_K=exD, deviation_K=q2D - exD, deviation_mK=1e3 * (q2D - exD),
        band_K=bandD, band_mK=1e3 * bandD, verdict=vD, band_verdict=bvD, note=noteD,
        temporal_triple=None,
        triple_absent_by_registration=("section 12 V3: 'completion -> instrument -> band (no "
                                       "triple; single level, stated)'"),
        spatial_triple={a: b for a, b in spatial["Q2"].items() if a != "values"},
        time_dir_read=keyD))
    res["reported_rows"].append(dict(
        row="V3-Q1", kind="REPORTED", quantity="Q1 at t = %g s" % tD, measured_K=q1D,
        reference_K=exD, deviation_mK=1e3 * (q1D - exD), band_mK_for_reference=1e3 * bandD))

    # ---- V4, V5: the balance instrument ------------------------------------
    bal, why = balance_C(df, nx_f, ny_f)
    if bal is None:
        refuse("the balance instrument could not read T20_LC_f: %s" % why)
    v4, bv4, note4 = apply_gate(bal["C"], 1.0 - GATES["balance_abs_max"],
                                1.0 + GATES["balance_abs_max"], None, True, "", [p2_nar])
    res["rows"].append(dict(row="V4", quantity="Q3 balance, UNPLANTED", case="T20_LC_f",
                            measured_C=bal["C"], deviation_from_1=abs(bal["C"] - 1.0),
                            band="|C - 1| <= %g" % GATES["balance_abs_max"],
                            verdict=v4, band_verdict=bv4, note=note4, detail=bal))
    # V5 is unreachable from a tree missing P10: the completion sweep above exits
    # NOT A RESULT first.  The row is written for the day the arm exists.
    balp, whyp = balance_C(os.path.join(root, "T20_LC_P10"), *_mesh("T20_LC_P10"))
    if balp is None:
        not_a_result("V5's PLANTED ARM could not be read (%s).\nSection 7.2: a REFUSAL of the "
                     "planted arm is an INSTRUMENT FAILURE and the whole rung is NOT A RESULT."
                     % whyp)
    diff = balp["C"] - bal["C"]
    v5, bv5, note5 = apply_gate(diff, GATES["planted_lo"], GATES["planted_hi"], None, True, "",
                                [p2_nar])
    res["rows"].append(dict(row="V5", quantity="Q3 balance, PLANTED +10 %", case="T20_LC_P10",
                            measured_difference=diff, C_planted=balp["C"], C_unplanted=bal["C"],
                            band="[%g, %g]" % (GATES["planted_lo"], GATES["planted_hi"]),
                            verdict=v5, band_verdict=bv5, note=note5))
    if v5 == "GATE FAIL":
        not_a_result("V5 measured C_planted - C_unplanted = %.6g, outside the registered "
                     "[%g, %g].\nSection 7.2: an instrument that cannot see a planted 10 %% is "
                     "not entitled to certify a 1 %% agreement, and the whole rung is NOT A "
                     "RESULT." % (diff, GATES["planted_lo"], GATES["planted_hi"]))

    # ---- P1, P3, P4 --------------------------------------------------------
    field = read_internal(df, key3, "T", nx_f * ny_f)
    surf = []
    for pt in CONV_PATCHES:
        surf.extend(read_patch(df, key3, "T", pt, nx_f))
    body_vals = list(field) + list(surf)
    tmean = sum(field) / len(field)
    p1 = (max(body_vals) - min(body_vals)) / (tmean - PH["T_inf"])
    res["reported_rows"].append(dict(
        row="P1", kind="GATE",
        quantity="lumped validity (T_max - T_min)/(T_mean - T_inf) at 3 tau",
        measured=p1, band="<= %g" % GATES["lumped_max"],
        verdict="PASS" if p1 <= GATES["lumped_max"] else "GATE FAIL",
        domain=("internal cells UNION the two convecting patch face values.  Section 5.2's "
                "registered prediction is built from the CENTRE-TO-SURFACE excess q'''L^2/(2k), "
                "so the surface must be inside the domain for the measurement to mean what the "
                "prediction predicts.  The frozen document does not spell the domain out; the "
                "internal-only variant is reported beside it and the gate is an order above the "
                "prediction, so the choice does not decide the row."),
        internal_only_variant=(max(field) - min(field)) / (tmean - PH["T_inf"])))
    p3_min, p3_where, p4_bad, prev = None, None, 0, None
    for name in written_times(df):
        v = read_internal(df, name, "T", nx_f * ny_f)
        if v is None:
            refuse("P3/P4: unreadable internal T at %s in T20_LC_f" % name)
        allv = list(v)
        for pt in CONV_PATCHES:
            pv = read_patch(df, name, "T", pt, nx_f)
            if pv is not None:
                allv.extend(pv)
        if p3_min is None or min(allv) < p3_min:
            p3_min, p3_where = min(allv), name
        if prev is not None:
            p4_bad += sum(1 for a, b in zip(prev, v) if b < a)
        prev = v
    res["reported_rows"].append(dict(
        row="P3", kind="GATE", quantity="no temperature below T_inf anywhere, any time",
        measured_min_K=p3_min, at_time=p3_where, T_inf=PH["T_inf"],
        verdict="PASS" if p3_min >= PH["T_inf"] else "GATE FAIL"))
    res["reported_rows"].append(dict(
        row="P4", kind="GATE", quantity="monotone rise in every cell under the constant source",
        n_nonmonotone_cell_steps=p4_bad, verdict="PASS" if p4_bad == 0 else "GATE FAIL"))

    # ---- the predictions are attached HERE and NOWHERE ELSE ----------------
    _attach_predictions(res, q_at)

    if not quiet:
        _print_report(res)
    with open(json_out, "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    print("gate json written: %s" % json_out)
    return EXIT_OK


def _attach_predictions(res, q_at):
    """R1-R6, and every other REGISTERED EXPECTATION.  Section 12: 'REPORTED
    beside the measured values, NEVER GATED.'

    THIS IS THE ONLY FUNCTION THAT READS `PREDICTIONS`, AND IT MAY NOT READ
    `GATES`.  Two source-level detectors in the selftest MEASURE both halves of
    that, each with a planted control.  A predicted value is an expectation about
    the derivation; grading against it instead of against its band would silently
    convert an expectation into a gate.  A measured residual inside the band but
    far from its prediction is a REPORTED FINDING about the derivation, and
    section 4.5 requires the results record to say so rather than pass it over."""
    for rowid, q, i in R_ROWS:
        t = SAMPLE_TIMES[i - 1]
        val = q_at("T20_LC_f", t)[0 if q == "Q1" else 1]
        resid_mK = 1e3 * (val - exact_T(t))
        pred = PREDICTIONS["net_resid_mK"][(q, i)]
        res["reported_rows"].append(dict(
            row=rowid, kind="REPORTED -- NEVER GATED",
            quantity="%s net residual at %d tau" % (q, i),
            measured_mK=resid_mK, predicted_mK=pred,
            measured_minus_predicted_mK=resid_mK - pred,
            prediction_provenance=PREDICTION_PROVENANCE[(q, i)], is_a_gate=False,
            note=("section 12 registers R1-R6 as REPORTED beside the measured values and NEVER "
                  "GATED.  No verdict is attached to this row and none may be.")))
    for r in res["reported_rows"]:
        if r["row"] == "P2":
            r["prediction_K"] = PREDICTIONS["invariance_predicted_K"]
            r["prediction_is"] = "REGISTERED EXPECTATION, NOT A GATE"
        elif r["row"] == "P1":
            r["prediction"] = PREDICTIONS["lumped_predicted"]
            r["prediction_is"] = "REGISTERED EXPECTATION, NOT A GATE"
        elif r["row"] == "V3-Q1":
            r["why_not_gated"] = (
                "section 6.4: Q1's constant model bias of %.3f mK is 34 %% of the band at 300 s, "
                "so Q1 here is REPORTED, NOT GATED, and the reason is written in the frozen "
                "document so it cannot later be read as a row quietly dropped."
                % PREDICTIONS["lumped_bias_mK"])
    for r in res["rows"]:
        if r["row"] == "V4":
            r["prediction"] = "|C - 1| < %g (REGISTERED EXPECTATION, NOT A GATE)" \
                % PREDICTIONS["balance_predicted"]
        if r.get("temporal_triple") and r.get("sample"):
            n = int(r["sample"].split()[0])
            r["p_predicted"] = PREDICTIONS["p_predicted"].get(n)
            r["GCI_pct_of_rise_predicted"] = PREDICTIONS["gci_predicted_pct"].get(n)
            r["predictions_are"] = "REGISTERED EXPECTATIONS, NOT GATES"
    for v in res["planted_zero_controls"].values():
        for arm in v.values():
            arm["floor_predicted_K"] = PREDICTIONS["floor_predicted_K"]
            arm["floor_prediction_is"] = "REGISTERED EXPECTATION, NOT A GATE"


def _print_report(res):
    print("")
    print("=" * 78)
    print("T20 -- GRADED ROWS (section 12's verdict map, and NO other row)")
    print("=" * 78)
    print("NON-BLIND: %s" % res["non_blind_disclosure"])
    print("")
    for r in res["rows"]:
        if "measured_K" in r:
            print("%-3s %-18s measured %.9f K  reference %.9f K  band +-%.4f mK  -> %s"
                  % (r["row"], "%s %s" % (r["quantity"], r.get("sample", "")), r["measured_K"],
                     r["reference_K"], r["band_mK"], r["verdict"]))
            print("      deviation %+.4f mK; band verdict %s" % (r["deviation_mK"], r["band_verdict"]))
            if r.get("temporal_triple"):
                print("      temporal triple (c/m/f, r=2, dim=1): %s" % fmt_tr(r["temporal_triple"]))
                if r.get("GCI_pct_of_rise") is not None:
                    print("      GCI_fine = %.6f %% OF THE RISE -- the registered basis.  The "
                          "module's GCI_pct is relative to ABSOLUTE T and is NOT the registered "
                          "gate." % r["GCI_pct_of_rise"])
            else:
                print("      %s" % r.get("triple_absent_by_registration", ""))
            if r.get("spatial_triple"):
                print("      spatial triple (Sc/f/Sf, r=2, dim=2), REPORTED ONLY: %s"
                      % fmt_tr(r["spatial_triple"]))
            if r["note"]:
                print("      %s" % r["note"])
        else:
            val = r.get("measured_C", r.get("measured_difference"))
            print("%-3s %-18s measured %.9g  band %s  -> %s"
                  % (r["row"], r["quantity"], val, r.get("band", "-"), r["verdict"]))
            if r["note"]:
                print("      %s" % r["note"])
    print("")
    print("-" * 78)
    print("REPORTED ROWS -- R1-R6 carry NO verdict against their predictions (section 12:")
    print("'REPORTED beside the measured values, never gated').")
    print("-" * 78)
    for r in res["reported_rows"]:
        if r["kind"].startswith("REPORTED --"):
            print("%-3s %-24s measured %+9.4f mK  predicted %+9.4f mK  delta %+9.4f mK"
                  % (r["row"], r["quantity"], r["measured_mK"], r["predicted_mK"],
                     r["measured_minus_predicted_mK"]))
            print("      provenance: %s" % r["prediction_provenance"])
        else:
            print("%-3s %-24s %s" % (r["row"], r["quantity"], r.get("verdict", "REPORTED")))
    print("")
    print("ROWS THE FROZEN VERDICT MAP DOES NOT CONTAIN, AND WHICH ARE THEREFORE NOT ROWS:")
    print("  %s" % res["rows_not_in_the_verdict_map"])


# ===========================================================================
# SELFTEST -- section 10, S1..S8.  SYNTHETIC TREES ONLY.
# ===========================================================================
class _RootWatch:
    """S8b/S8c.  Records every filesystem read under `root` except `allow`."""

    def __init__(self, root, allow=()):
        self.root = os.path.realpath(root)
        self.allow = set(os.path.realpath(a) for a in allow)
        self.hits = []
        self._in = False

    def _note(self, p):
        if self._in:
            return
        self._in = True
        try:
            if isinstance(p, bytes):
                p = p.decode("utf-8", "replace")
            if not isinstance(p, str):
                p = os.fspath(p)
            ap = os.path.realpath(p)
            if (ap == self.root or ap.startswith(self.root + os.sep)) and ap not in self.allow:
                self.hits.append(ap)
        except Exception:
            pass
        finally:
            self._in = False

    def __enter__(self):
        import builtins
        import glob as _glob
        self._saved = (builtins.open, os.listdir, os.scandir, os.path.isfile,
                       os.path.isdir, os.path.exists, os.stat, _glob.glob)
        w = self

        def wrap(fn):
            def g(path, *a, **k):
                if isinstance(path, (str, bytes)) or hasattr(path, "__fspath__"):
                    w._note(path)
                return fn(path, *a, **k)
            return g
        builtins.open = wrap(self._saved[0])
        os.listdir = wrap(self._saved[1])
        os.scandir = wrap(self._saved[2])
        os.path.isfile = wrap(self._saved[3])
        os.path.isdir = wrap(self._saved[4])
        os.path.exists = wrap(self._saved[5])
        os.stat = wrap(self._saved[6])
        _glob.glob = wrap(self._saved[7])
        return self

    def __exit__(self, *exc):
        import builtins
        import glob as _glob
        (builtins.open, os.listdir, os.scandir, os.path.isfile, os.path.isdir,
         os.path.exists, os.stat, _glob.glob) = self._saved
        return False


def _here_refs_in_selftest(src=None):
    """S8d.  Counts references to the name `HERE` inside the selftest functions.
    analyse_t18.py's `grade(HERE, ...)` limb fired on its own LIVE tree and
    produced a file byte-identical to the real gate output; that single reference
    is the whole defect this detector exists to make impossible here."""
    tree = ast.parse(src if src is not None else open(__file__).read())
    n = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in (
                "_limbs", "selftest", "_populate_run_root", "_forge", "_forge_rung"):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name) and sub.id == "HERE":
                    n += 1
    return n


def _name_refs_in(src, fnames, target):
    tree = ast.parse(src if src is not None else open(__file__).read())
    n = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in fnames:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name) and sub.id == target:
                    n += 1
    return n


GATING_FUNCS = ("apply_gate", "grade", "completion", "planted_zero_control", "balance_C",
                "triple_of")
REPORTING_FUNCS = ("_attach_predictions",)

_HDR = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class volScalarField;\n"
        "    object T;\n}\n\ndimensions [0 0 0 1 0 0 0];\n\n")
# A first-order-in-time lag, so a FORGED temporal triple is CONVERGING with p = 1
# BY CONSTRUCTION -- which is what `ddtSchemes default Euler` must give.  Without
# it the three forged levels would be identical, the triple would classify EXACT,
# and every band limb would be testing rule 5's clause (2) instead of the band.
LAG_PER_DT = -1.5e-4        # K per second of deltaT


def _wf(path, internal, surf, prec=12):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fmt = "%%.%dg" % prec
    body = [_HDR, "internalField   nonuniform List<scalar> \n%d\n(\n" % len(internal)]
    body += [(fmt % v) + "\n" for v in internal]
    body.append(")\n;\n\nboundaryField\n{\n")
    for pt in CONV_PATCHES:
        body.append("    %s\n    {\n        type externalWallHeatFluxTemperature;\n"
                    "        refValue uniform 293;\n        value uniform %s;\n    }\n"
                    % (pt, fmt % surf))
    body.append("    \"endLo|endHi\"\n    {\n        type zeroGradient;\n    }\n}\n")
    open(path, "w").write("".join(body))


def _forge(root, case, nx, ny, deltaT, endTime, steps, mean_err=0.0, surf_err=0.0,
           src_scale=1.0, prec=12, rc="0", end_line=True, last_time=None, drop_T=False,
           n_exec=None, stale=False, stale_equal=False, spread=0.0, surf_dip=False,
           nonmono=False):
    """A synthetic case tree that satisfies section 8 BY CONSTRUCTION unless a
    keyword breaks EXACTLY ONE conjunct.  Fields follow the exact lumped solution
    plus a first-order temporal lag, so the value control is a real value control
    and the temporal triple is genuinely CONVERGING."""
    d = os.path.join(root, case)
    times, t = [0.0], 150.0
    while t <= endTime + 1e-9:
        times.append(t)
        t += 150.0
    if times[-1] < endTime - 1e-9:
        times.append(endTime)
    if last_time is not None:
        times[-1] = last_time
    lag = LAG_PER_DT * deltaT
    for k, tt in enumerate(times):
        nm = "%g" % tt
        rise = DT_SS * (1.0 - math.exp(-tt / TAU)) * src_scale
        base = PH["T_inf"] + rise + (lag if tt > 0 else 0.0)
        cells = []
        for j in range(ny):
            y = (j + 0.5) / ny - 0.5
            cells.extend([base + mean_err + spread * (0.25 - y * y) for _ in range(nx)])
        surf = base + surf_err
        if tt == 0.0:
            cells, surf = [PH["T_inf"]] * (nx * ny), PH["T_inf"]
        # P3's control is sized to cross T_inf and NOTHING ELSE: a full 1 K dip
        # moves E_conv by ~1.4 % of E_src, which drags V5's planted difference out
        # of its band and turns a P3 control into a V5 refusal.  1 nK below T_inf
        # fires P3 and moves nothing else measurably.
        if surf_dip and k == 1:
            surf = PH["T_inf"] - 1.0e-9
        # P4's control must exceed the rise BETWEEN two writes (~0.31 K at t=150
        # to 300) or the cell is still increasing and P4 correctly reports PASS.
        # 0.5 K at t = 300 breaks monotonicity, stays above T_inf so P3 is
        # untouched, and touches neither a sample time nor endTime.
        if nonmono and k == 2:
            cells[0] -= 0.5
        if drop_T and k == len(times) - 1:
            os.makedirs(os.path.join(d, nm, REGION), exist_ok=True)
            continue
        _wf(os.path.join(d, nm, REGION, "T"), cells, surf, prec)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write(
        "deltaT %g;\nendTime %g;\nwriteInterval 150;\nwriteFormat ascii;\n"
        "writePrecision %d;\ntimePrecision 12;\nadjustTimeStep no;\n"
        % (deltaT, endTime, prec))
    ne = n_exec if n_exec is not None else steps
    log = ["ExecutionTime = %g s\n" % (0.001 * i) for i in range(ne)]
    if end_line:
        log.append("End\n")
    open(os.path.join(d, "log.solve"), "w").write("".join(log))
    open(os.path.join(root, "STATUS.%s" % case), "w").write(
        "case=%s\nrc=%s\nwall_s=1\nranks=1\ncore_min=0.017\nnote=synthetic\n" % (case, rc))
    _time.sleep(0.003)
    if stale:
        os.utime(_field_path(d, "0", "T"), None)        # break conjunct 6 and only that
    else:
        for nm in os.listdir(d):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", nm) and float(nm) > 0:
                fp = _field_path(d, nm, "T")
                if os.path.isfile(fp):
                    os.utime(fp, None)
    if stale_equal:
        # THE STRICTNESS ARM, AND IT WAS ADDED BECAUSE A MUTATION CONTROL PROVED
        # IT WAS MISSING.  The `stale` arm above makes the endTime field STRICTLY
        # OLDER than 0/T, which both `tf > t0` and `tf >= t0` reject -- so it does
        # not test that rule 4's "NEWER than" is STRICT, and a mutant that relaxed
        # the guard to `>=` passed the selftest untouched.  This arm sets the
        # endTime field's mtime EXACTLY EQUAL to 0/T's, which only the strict
        # guard rejects.  It is also the physically realistic case: a run fast
        # enough to finish inside one filesystem mtime tick lands here.
        ts_all = sorted((n for n in os.listdir(d)
                         if re.fullmatch(r"[0-9]+(\.[0-9]+)?", n) and float(n) > 0), key=float)
        if ts_all:
            t0 = os.stat(_field_path(d, "0", "T")).st_mtime
            fp = _field_path(d, ts_all[-1], "T")
            if os.path.isfile(fp):
                os.utime(fp, (t0, t0))
    return d


def _forge_rung(root, per=None, **kw):
    """All SEVEN registered cases at their frozen ladder settings.  T20_LC_P10
    defaults to a GENUINE +10 % arm, so the default forged rung is a healthy rung
    and a limb that wants an unhealthy one must say so."""
    per = per or {}
    for case, f in FROZEN_CASES.items():
        nx, ny = _mesh(case)
        a = dict(kw)
        if case == "T20_LC_P10" and "src_scale" not in a:
            a["src_scale"] = 1.10
        a.update(per.get(case, {}))
        _forge(root, case, nx, ny, f["deltaT"], f["endTime"], f["steps"], **a)


def _populate_run_root(root):
    """S8a pass B: a run root FULLY POPULATED at the registered ladder.  Nothing in
    the limb set is allowed to notice."""
    _forge_rung(root)


def _limbs(run_root):
    """THE WHOLE LIMB SET.  Every limb forges its own synthetic tree in a scratch
    directory it creates and removes.  `run_root` is handed in ONLY so that S8 can
    MEASURE invariance: no limb may read, stat or glob it."""
    fails, probe = [], []

    def ck(label, ok, extra=""):
        print("  [%s] %s%s" % ("ok  " if ok else "FAIL", label, ("  " + extra) if extra else ""))
        if not ok:
            fails.append(label)
        return ok

    def run(**kw):
        tmp = tempfile.mkdtemp(prefix="t20forge_")
        try:
            _forge_rung(tmp, **kw)
            out = os.path.join(tmp, "gate.json")
            code, LAST_REFUSAL[0] = None, ""
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    code = grade(tmp, out, quiet=True)
            except SystemExit as e:
                code = e.code
            r = json.load(open(out)) if os.path.isfile(out) else None
            return code, r, os.path.isfile(out), LAST_REFUSAL[0]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def verdicts(r, *rows):
        if not r:
            return None
        return sorted(set(x["verdict"] for x in r["rows"] if x["row"] in rows))

    # -- S0: THE ROW SET IS THE FROZEN ROW SET, AND NOTHING ELSE -------------
    impl = sorted(set(GATED_ROW_IDS + [x[0] for x in R_ROWS]))
    ck("S0a the implemented row set == the row ids PARSED FROM SECTION 12 (%s)"
       % ", ".join(sorted(set(FROZEN_ROW_IDS))), impl == sorted(set(FROZEN_ROW_IDS)))
    ck("S0b NEITHER T20_LC_c NOR T20_LC_m appears in any section-12 row -- both are 'triple "
       "only' in section 9, so six completed cases do NOT make six graded rows",
       (not re.search(r"^\| \*\*[VPR][0-9–R]*\*\* \|.*T20_LC_[cm]`", _FROZEN_TEXT, re.M))
       and FROZEN_CASES["T20_LC_c"]["graded"] == "triple only"
       and FROZEN_CASES["T20_LC_m"]["graded"] == "triple only")
    ck("S0c the section 9 run-set table registers SEVEN cases, including the unbuilt T20_LC_P10",
       len(FROZEN_CASES) == 7 and "T20_LC_P10" in FROZEN_CASES)

    # -- the healthy forged rung: the value control --------------------------
    code, r, wrote, _ = run()
    tr_ok = r and all(x["temporal_triple"]["state"] == "CONVERGING"
                      for x in r["rows"] if x.get("temporal_triple"))
    p_ok = r and all(abs(x["temporal_triple"]["order"] - 1.0) < 1e-9
                     for x in r["rows"] if x.get("temporal_triple"))
    all_pass = verdicts(r, *GATED_ROW_IDS)
    ck("VALUE CONTROL: the exact lumped solution plus a first-order lag on the registered ladder "
       "grades every V row PASS with a CONVERGING temporal triple at p = 1.000",
       code == EXIT_OK and tr_ok and p_ok and all_pass == ["PASS"],
       "code=%r verdicts=%s" % (code, all_pass))
    sp = r["spatial_triple"]["Q1"]["state"] if r else None
    ck("the SPATIAL triple on the same tree classifies %s and is REPORTED, never gated -- "
       "section 5.2 pre-registers exactly this and rule 5 is NOT engineered around it" % sp,
       sp == "EXACT" and r["spatial_triple"]["Q1"].get("GCI_pct") is None)
    probe.append(("value-control", code, all_pass, sp))

    # -- S1: BOTH SIGNS of every drift ---------------------------------------
    # The offset is applied to ALL levels, so the TRIPLE is untouched and the limb
    # tests the BAND and nothing else.  A one-sided threshold passes a two-sided
    # band only by luck; T15's `0.5*ref` is the failure this limb prevents.
    s1 = []
    band3 = GATES["band_K"][3]
    for tag, mult, want in (("+1.5 x band", 1.5, "GATE FAIL"), ("-1.5 x band", -1.5, "GATE FAIL"),
                            ("+0.5 x band", 0.5, "PASS"), ("-0.5 x band", -0.5, "PASS")):
        code, r, _w, _m = run(mean_err=mult * band3, surf_err=mult * band3)
        got = verdicts(r, "V1", "V2")
        s1.append((tag, got))
        ck("S1 %-12s -> V1/V2 %s (want [%s])" % (tag, got, want), got == [want])
    probe.append(("S1", s1))

    # -- S2: BLIND reader must REFUSE ----------------------------------------
    saved = globals()["read_internal"]
    globals()["read_internal"] = lambda cd, t, nm, nc: [295.0] * nc
    try:
        code, r, wrote, msg = run()
    finally:
        globals()["read_internal"] = saved
    ck("S2 BLIND reader (a constant vector independent of the file bytes) -> exit 2 REFUSE with "
       "the BLIND message, and NO verdict is produced",
       code == EXIT_REFUSE and not wrote and "BLIND" in msg, "code=%r" % (code,))
    probe.append(("S2", code, wrote, "BLIND" in msg))

    # -- S3: NOISY reader must REFUSE (the negative arm) ---------------------
    saved = globals()["Q1_mean"]
    state = {"n": 0}

    def noisy(*a, **k):
        v = saved(*a, **k)
        state["n"] += 1
        return v if state["n"] % 2 else (v + 5e-14 if v else v)
    globals()["Q1_mean"] = noisy
    try:
        code, r, wrote, msg = run()
    finally:
        globals()["Q1_mean"] = saved
    ck("S3 NOISY reader (one ULP of jitter on the second call) -> the NEGATIVE ARM fires on a "
       "non-zero dneg, exit 2.  This is the limb T3 did not have",
       code == EXIT_REFUSE and not wrote and "NOISY" in msg, "code=%r" % (code,))
    probe.append(("S3", code, wrote, "NOISY" in msg))

    # -- S4: UNDERSIZED plant must REFUSE (clause 5) -------------------------
    saved = globals()["_plant_internal"]

    def one_cell(path, mag, prec):
        lines = open(path).read().splitlines(True)
        for i, ln in enumerate(lines):
            if "internalField" in ln and "nonuniform" in ln:
                for j in range(i, min(i + 5, len(lines))):
                    if lines[j].strip() == "(":
                        lines[j + 1] = ("%%.%dg\n" % prec) % (float(lines[j + 1].strip()) + mag)
                        open(path, "w").write("".join(lines))
                        return 1
        return 0
    globals()["_plant_internal"] = one_cell
    try:
        code, r, wrote, msg = run()
    finally:
        globals()["_plant_internal"] = saved
    ck("S4 UNDERSIZED plant (1 cell instead of 240) -> CLAUSE 5 fires (seen[PLANT] < %g x PLANT). "
       "Proves the sizing test is live, not decorative" % GATES["plant_sizing_frac"],
       code == EXIT_REFUSE and not wrote and "CLAUSE 5" in msg, "code=%r" % (code,))
    probe.append(("S4", code, wrote, "CLAUSE 5" in msg))

    # -- S5: the FLOOR-TIED refusal (clause 8) -------------------------------
    # THE REGISTERED LIMB, AND A MEASURED DEFECT IN IT, RECORDED RATHER THAN
    # REPAIRED.  Section 10 S5 registers writePrecision 4 and attributes the
    # refusal to clause 8.  MEASURED: at precision 4 the REGISTERED PLANT ITSELF
    # is invisible, so CLAUSE 5 fires first -- section 7.1 introduces clause 8 as
    # "in addition to clause 5", so clause 5 has precedence and clause 8 is never
    # reached.  The registered outcome (REFUSE) holds; the registered ATTRIBUTION
    # does not.
    #
    # AND CLAUSE 8 HAS A NARROW REACHABLE WINDOW, WHICH IS WORTH RECORDING.  It
    # fires only when the demonstrated floor exceeds 1.9e-04 K, while the
    # registered ladder's magnitudes step 1e-02, PLANT = 1.234e-03, 1e-04.  The
    # ceiling sits in the GAP between PLANT and 1e-04, so the only floor that both
    # passes clause 5 and trips clause 8 is PLANT itself -- which needs a field
    # whose write resolution lies strictly between 1e-04 and 1.234e-03.  S5b
    # constructs exactly that: writePrecision 6 (OpenFOAM's OWN DEFAULT, the hazard
    # section 4.4 clause 1 registers) with the field value shifted onto the centre
    # of its own 1e-03 rounding cell, so a 1e-04 plant cannot cross the cell edge
    # and PLANT can.  BOTH arms must REFUSE; only S5b can attribute to clause 8.
    code, r, wrote, msg4 = run(prec=4)
    ck("S5a writePrecision 4 (the limb exactly as registered in section 10) -> REFUSE",
       code == EXIT_REFUSE and not wrote, "clause fired: %s"
       % ("5" if "CLAUSE 5" in msg4 else "8" if "CLAUSE 8" in msg4 else "?"))
    base3 = exact_T(SAMPLE_TIMES[2]) + LAG_PER_DT * FROZEN_CASES["T20_LC_f"]["deltaT"]
    onto_grid = round(base3, 3) - base3          # centre of the 1e-03 rounding cell
    code6, r6, wrote6, msg6 = run(prec=6, mean_err=onto_grid, surf_err=onto_grid)
    ck("S5b writePrecision 6 (OpenFOAM's DEFAULT) with the value on its 1e-03 rounding-cell "
       "centre -> the demonstrated floor is the PLANT itself, above the registered %.1g K "
       "ceiling, and CLAUSE 8 fires" % GATES["floor_max_K"],
       code6 == EXIT_REFUSE and not wrote6 and "CLAUSE 8" in msg6,
       "code=%r clause=%s" % (code6, "8" if "CLAUSE 8" in msg6 else
                              "5" if "CLAUSE 5" in msg6 else "?"))
    probe.append(("S5", code, "CLAUSE 5" in msg4, code6, "CLAUSE 8" in msg6))

    # -- S6: the balance instrument sees the plant, BOTH DIRECTIONS ----------
    # Driven on FORGED PAIRS through balance_C directly, which is what section 10
    # S6 registers ("a forged pair of trees differing only by a +10 % source").
    def pair(scale):
        tmp = tempfile.mkdtemp(prefix="t20bal_")
        try:
            f = FROZEN_CASES["T20_LC_f"]
            nx, ny = _mesh("T20_LC_f")
            _forge(tmp, "A", nx, ny, f["deltaT"], f["endTime"], f["steps"])
            _forge(tmp, "B", nx, ny, f["deltaT"], f["endTime"], f["steps"], src_scale=scale)
            a, _e = balance_C(os.path.join(tmp, "A"), nx, ny)
            b, _e = balance_C(os.path.join(tmp, "B"), nx, ny)
            return b["C"] - a["C"]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    d10, d00 = pair(1.10), pair(1.00)
    ck("S6a a forged pair differing ONLY by a +10 %% source -> C_planted - C_unplanted in "
       "[%g, %g]" % (GATES["planted_lo"], GATES["planted_hi"]),
       GATES["planted_lo"] <= d10 <= GATES["planted_hi"], "measured %.6f" % d10)
    ck("S6b a forged pair differing by 0 % -> difference < 0.005, so the instrument is shown "
       "able to report 'no plant' as well as 'plant'", abs(d00) < 0.005, "measured %.3e" % d00)
    probe.append(("S6", d10, d00))

    # -- S7: the six completion limbs, one conjunct each ---------------------
    s7 = []
    for tag, kw in (("conjunct 1: rc != 0", dict(rc="1")),
                    ("conjunct 2: no End line", dict(end_line=False)),
                    ("conjunct 3: last time 4494 != 4500", dict(last_time=4494.0)),
                    ("conjunct 4: T missing at endTime", dict(drop_T=True)),
                    ("conjunct 5: 2999 lines vs registered 3000", dict(n_exec=2999)),
                    ("conjunct 6: a field OLDER than 0/T (age guard)", dict(stale=True)),
                    ("conjunct 6 STRICTNESS: a field the SAME AGE as 0/T", dict(stale_equal=True))):
        code, r, wrote, _m = run(per={"T20_LC_f": kw})
        s7.append((tag, code, wrote))
        ck("S7 %-46s -> RUNG NOT A RESULT, no graded value, no json" % tag,
           code == EXIT_NOT_A_RESULT and not wrote, "code=%r" % (code,))
    probe.append(("S7", s7))

    # -- V5 ABSENT IS FATAL.  THIS IS THE LIVE CONDITION. --------------------
    tmp = tempfile.mkdtemp(prefix="t20nop10_")
    try:
        _forge_rung(tmp)
        shutil.rmtree(os.path.join(tmp, "T20_LC_P10"))
        os.remove(os.path.join(tmp, "STATUS.T20_LC_P10"))
        out = os.path.join(tmp, "gate.json")
        code, LAST_REFUSAL[0] = None, ""
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                code = grade(tmp, out, quiet=True)
        except SystemExit as e:
            code = e.code
        wrote, msg = os.path.isfile(out), LAST_REFUSAL[0]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ck("V5 ABSENT (T20_LC_P10 removed; the other SIX are COMPLETE) -> RUNG NOT A RESULT, no json, "
       "no row graded, and the message names V5 -- an unbuildable arm may NEVER become a clean "
       "sheet", code == EXIT_NOT_A_RESULT and not wrote and "V5" in msg,
       "code=%r wrote=%r" % (code, wrote))
    probe.append(("V5-absent", code, wrote, "V5" in msg))

    # -- the EXACT-triple limb: NOT engineered around ------------------------
    tr = triple_of([1.0, 1.0, 1.0], REFINEMENT, 1)
    v, bv, _n = apply_gate(1.0, 0.0, 2.0, tr, True, "")
    ck("an EXACT temporal triple (three identical values) -> NOT A RESULT even though the BAND "
       "verdict is %s, and NO GCI is quoted beside it" % bv,
       v == "NOT A RESULT" and tr["state"] == "EXACT" and tr.get("GCI_pct") is None)
    probe.append(("exact", v, tr["state"], tr.get("GCI_pct")))

    # -- the ONE-WAY property -------------------------------------------------
    trc = triple_of([1.0 + 4e-3, 1.0 + 1e-3, 1.0], REFINEMENT, 1)
    v1, _b1, _n1 = apply_gate(1.0, 0.9, 1.1, trc, True, "")
    v2, bv2, _n2 = apply_gate(5.0, 0.9, 1.1, trc, False, "forced")
    ck("the gate is ONE WAY: a CONVERGING triple inside the band gives %s, and a failed gate (1) "
       "turns a %s into %s -- never the reverse" % (v1, bv2, v2),
       v1 == "PASS" and bv2 == "GATE FAIL" and v2 == "NOT A RESULT")

    # -- GATE / PREDICTION separation, MEASURED AT THE SOURCE -----------------
    src = open(__file__).read()
    n_pred = _name_refs_in(src, GATING_FUNCS, "PREDICTIONS")
    n_pred_p = _name_refs_in("def apply_gate(a):\n    return PREDICTIONS['x']\n",
                             GATING_FUNCS, "PREDICTIONS")
    ck("GATE/PREDICTION separation (a): `PREDICTIONS` is referenced %d times inside the GATING "
       "functions %s; the SAME detector on a planted source returns %d, so the zero is PLANTED, "
       "not blind" % (n_pred, list(GATING_FUNCS), n_pred_p), n_pred == 0 and n_pred_p == 1)
    n_gat = _name_refs_in(src, REPORTING_FUNCS, "GATES")
    n_gat_p = _name_refs_in("def _attach_predictions(a, b):\n    return GATES['x']\n",
                            REPORTING_FUNCS, "GATES")
    ck("GATE/PREDICTION separation (b): `GATES` is referenced %d times inside the prediction "
       "reporter %s; the planted control returns %d" % (n_gat, list(REPORTING_FUNCS), n_gat_p),
       n_gat == 0 and n_gat_p == 1)
    ck("GATE/PREDICTION separation (c): the two containers share no key",
       not (set(GATES) & set(PREDICTIONS)))
    code, r, _w, _m = run()
    rrows = [x for x in (r["reported_rows"] if r else []) if x["row"].startswith("R")]
    ck("GATE/PREDICTION separation (d): all %d R rows carry kind 'REPORTED -- NEVER GATED', "
       "is_a_gate False and NO verdict key" % len(rrows),
       len(rrows) == 6 and all(x["kind"] == "REPORTED -- NEVER GATED" and x["is_a_gate"] is False
                               and "verdict" not in x for x in rrows))
    ck("R1-R6 provenance is printed per row: %d REGISTERED VERBATIM, %d DERIVED FROM REGISTERED "
       "(section 4.5 says 'six' and tabulates four)"
       % (sum("VERBATIM" in x["prediction_provenance"] for x in rrows),
          sum("DERIVED" in x["prediction_provenance"] for x in rrows)),
       sum("VERBATIM" in x["prediction_provenance"] for x in rrows) == 4
       and sum("DERIVED" in x["prediction_provenance"] for x in rrows) == 2)
    probe.append(("sep", n_pred, n_pred_p, n_gat, n_gat_p, len(rrows)))

    # -- P3 and P4, one control each -----------------------------------------
    code, r, _w, _m = run(per={"T20_LC_f": dict(surf_dip=True)})
    got = {x["row"]: x.get("verdict") for x in (r["reported_rows"] if r else [])}
    ck("P3 control: a surface value 1 nK BELOW T_inf at one written time -> P3 GATE FAIL, P4 PASS",
       got.get("P3") == "GATE FAIL" and got.get("P4") == "PASS", "%s" % got)
    code, r, _w, _m = run(per={"T20_LC_f": dict(nonmono=True)})
    got = {x["row"]: x.get("verdict") for x in (r["reported_rows"] if r else [])}
    ck("P4 control: one cell stepping DOWN by 0.5 K between two writes -> P4 GATE FAIL, P3 PASS",
       got.get("P4") == "GATE FAIL" and got.get("P3") == "PASS", "%s" % got)
    code, r, _w, _m = run(per={"T20_LC_Sf": dict(mean_err=10.0 * GATES["band_K"][3],
                                                 surf_err=10.0 * GATES["band_K"][3])})
    got = {x["row"]: x.get("verdict") for x in (r["reported_rows"] if r else [])}
    ck("P2 control: T20_LC_Sf displaced by 10 x band -> P2 GATE FAIL, and V1/V2/V3 move ONE WAY "
       "to NOT A RESULT (section 5.2's registered consequence, not GATE FAIL)",
       got.get("P2") == "GATE FAIL" and verdicts(r, "V1", "V2", "V3") == ["NOT A RESULT"],
       "P2=%s V=%s" % (got.get("P2"), verdicts(r, "V1", "V2", "V3")))
    probe.append(("P-controls", got.get("P2")))

    # -- the pin fires on a moved gate ---------------------------------------
    tmpp = tempfile.mkdtemp(prefix="t20pin_")
    fired = False
    try:
        bad = os.path.join(tmpp, "moved.md")
        open(bad, "w").write(_FROZEN_TEXT.replace("0.0189636", "0.0289636"))
        try:
            pin(bad, PREREG_SHA256, "a MUTATED pre-registration")
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmpp, ignore_errors=True)
    ck("a pre-registration with ONE BAND DIGIT changed fails the sha256 pin -> REFUSE.  This is "
       "the only mechanism by which 'no gate moved' is a measurement rather than a claim", fired)

    # -- no ast.Assert anywhere (L-332) --------------------------------------
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ck("AST assert count in this file = %d (the counter sees a planted assert: %d)" % (n0, n1),
       n0 == 0 and n1 == 1)

    return dict(fails=fails, probe=probe)


def selftest():
    print("analyse_t20 --selftest")
    print("NON-BLIND DISCLOSURE: T20's gated grading is NO LONGER ANALYST-BLIND; the bands were")
    print("frozen at %s BEFORE the predictions were read, so rule 2 survives intact."
          % PREREG_COMMIT[:8])
    print("Section 10.1 S8: the limb set runs TWICE (empty vs fully populated synthetic run root)")
    print("and the two outcome structures must be byte-identical.  NO limb touches a live tree.")
    live = os.path.dirname(os.path.abspath(__file__))
    results, watched = {}, {}
    for tag, populate in (("A/EMPTY-run-root", False), ("B/POPULATED-run-root", True)):
        rr = tempfile.mkdtemp(prefix="t20_rr_")
        try:
            if populate:
                _populate_run_root(rr)
            npop = len(os.listdir(rr))
            print("-- pass %s (%d entries in the synthetic run root) --" % (tag, npop))
            with _RootWatch(live, allow=(REG_PATH, PROSE_PATH, os.path.abspath(__file__))) as pw, \
                    _RootWatch(rr) as rw:
                # RULE 3.  Plant a read each watcher MUST see before its zero is
                # allowed to mean anything.  Both probe paths are chosen NOT to
                # exist, so nothing is learned about either tree -- only about the
                # watchers themselves.
                os.path.isfile(os.path.join(rr, "PLANTED_PROBE_NOT_A_CASE"))
                os.path.isfile(os.path.join(live, "T20_LC_PLANTED_PROBE", "not_a_file"))
                planted = (len(rw.hits), len(pw.hits))
                rw.hits, pw.hits = [], []
                res = _limbs(rr)
            results[tag] = res
            watched[tag] = dict(planted=planted, rr_hits=sorted(set(rw.hits)),
                                live_hits=sorted(set(pw.hits)), npop=npop)
        finally:
            shutil.rmtree(rr, ignore_errors=True)

    fails = list(results["A/EMPTY-run-root"]["fails"])
    for lbl in results["B/POPULATED-run-root"]["fails"]:
        if lbl not in fails:
            fails.append(lbl)
    print("S8 -- the invariance and access measurements:")
    a = json.dumps(results["A/EMPTY-run-root"], sort_keys=True, default=str)
    b = json.dumps(results["B/POPULATED-run-root"], sort_keys=True, default=str)
    ok = (a == b)
    print("  [%s] S8a INVARIANCE: the outcome structure over an EMPTY run root (0 entries) is "
          "BYTE-IDENTICAL to the one over a FULLY POPULATED run root (%d entries, all seven "
          "registered cases)"
          % ("ok  " if ok else "FAIL", watched["B/POPULATED-run-root"]["npop"]))
    if not ok:
        fails.append("S8a-invariance")
        print("      A: %s\n      B: %s" % (a[:400], b[:400]))
    ok = all(watched[t]["planted"][0] >= 1 and watched[t]["planted"][1] >= 1 for t in watched)
    print("  [%s] S8b/S8c PLANTED CONTROL (rule 3): a deliberate read under each watched root was "
          "SEEN -- run-root watcher %d, live-tree watcher %d.  A zero from a watcher not shown "
          "able to see a non-zero would not be evidence."
          % ("ok  " if ok else "FAIL", watched["A/EMPTY-run-root"]["planted"][0],
             watched["A/EMPTY-run-root"]["planted"][1]))
    if not ok:
        fails.append("S8-planted-control")
    ok = all(not watched[t]["rr_hits"] for t in watched)
    print("  [%s] S8b: NO limb read, listed or stat-ed the synthetic run root in either pass "
          "(%d + %d recorded reads)"
          % ("ok  " if ok else "FAIL", len(watched["A/EMPTY-run-root"]["rr_hits"]),
             len(watched["B/POPULATED-run-root"]["rr_hits"])))
    if not ok:
        fails.append("S8b-run-root-touched")
        print("      touched: %s" % watched["A/EMPTY-run-root"]["rr_hits"][:6])
    ok = all(not watched[t]["live_hits"] for t in watched)
    print("  [%s] S8c: NO limb read anything under the LIVE T20_runs tree beyond the pinned "
          "instruments (%d recorded reads).  This is the clause analyse_t18.py lacked, whose "
          "grade(HERE, ...) limb fired on its own live tree."
          % ("ok  " if ok else "FAIL", len(watched["A/EMPTY-run-root"]["live_hits"])))
    if not ok:
        fails.append("S8c-live-tree-touched")
        print("      touched: %s" % watched["A/EMPTY-run-root"]["live_hits"][:6])
    n_here = _here_refs_in_selftest()
    n_planted = _here_refs_in_selftest("def _limbs(run_root):\n    return grade(HERE, run_root)\n")
    ok = (n_here == 0 and n_planted == 1)
    print("  [%s] S8d: `HERE` references inside the selftest functions = %d (the SAME detector on "
          "a planted `grade(HERE, ...)` source returns %d, so the zero is planted, not blind)"
          % ("ok  " if ok else "FAIL", n_here, n_planted))
    if not ok:
        fails.append("S8d-here-detector")
    print("SELFTEST %s (%d failed)%s"
          % ("PASS" if not fails else "FAIL", len(fails),
             ("" if not fails else ": " + "; ".join(fails))))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser(
        description="T20 comparator.  NOT ANALYST-BLIND; see the disclosure at the top of the "
                    "file.  A registered case missing or incomplete makes the RUNG NOT A RESULT "
                    "and there is no flag that bypasses it.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=None, help="run root to grade; defaults to this directory")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    root = a.root or HERE
    print("T20 comparator, frozen pre-registration %s (sha256 %s...)"
          % (PREREG_COMMIT[:8], PREREG_DIGEST[:16]))
    print("NON-BLIND: the pre-registered predictions were read before this comparator was "
          "written; the bands were frozen before that.")
    return grade(root, a.json or os.path.join(root, "gate_t20.json"))


if __name__ == "__main__":
    sys.exit(main())
