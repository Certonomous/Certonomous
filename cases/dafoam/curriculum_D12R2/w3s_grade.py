#!/usr/bin/env python3
"""W3S ARM A (`GSCAN`) COMPARATOR.  SUCCESSOR INSTRUMENT -- THE PARENT IS NOT EDITED.

PARENT: `d12y_grade_w3.py`, md5 3950d30fd09c9b56213a02f5e9864e20, FROZEN.
CLAUDE.md rule 6 binds it: a frozen file is never edited, so this is a NEW FILE, exactly
as `d12y_grade_w3.py` itself succeeded the W2R comparator rather than editing it.  The
parent's md5 is PINNED here and CHECKED at every invocation before the parent is imported,
and this file CALLS the parent's own functions where it reuses them -- it does not copy
them.  A copy drifts; a call cannot.

WHAT THIS FILE IS FOR.  W3S Arm A buys |g(W)| at three windows in one run root, so its
manifest rows DELIBERATELY DISAGREE ON W.  The parent's `_w_from_record` REFUSES exactly
that (`W3-A2: manifest rows disagree on W`), and that refusal exists because of
W2R-GRADER-DEF-1, where a comparator graded the wrong window silently.  THAT REFUSAL IS
NOT RELAXED HERE.  It is replaced, for `--gscan` data only, by a per-leg binding that is
strictly more constrained -- see THE NARROWING, below, and `--selftest-narrowing`, which
DRIVES it against the parent's own function rather than asserting it in prose.

THE NARROWING, STATED HONESTLY AND IN THE ONLY FORM THAT IS TRUE.
The brief that commissioned this file asked for "anything the inherited gate refuses,
`--gscan` also refuses".  THAT SENTENCE IS NOT SATISFIABLE AND SAYING SO IS PART OF THE
DELIVERABLE: the inherited gate refuses Arm A's own manifest, so a `--gscan` that also
refused it would grade nothing.  The provable statement, which this file implements and
`--selftest-narrowing` drives in BOTH directions, is:

  (N1) ON THE DOMAIN THE INHERITED GATE GOVERNS -- window-homogeneous row sets --
       `--gscan` REFUSES EVERYTHING.  Not a superset of the parent's refusals: the WHOLE
       domain, the parent's accepts included.  Driven, with the parent's accepting inputs
       exhibited so the direction is not vacuous.
  (N2) OFF THAT DOMAIN, EVERY ROW IS STILL SUBJECTED TO THE PARENT'S STRUCTURAL LIMBS,
       INSIDE ITS OWN LEG.  Five of the parent's six limbs (row carries W; W parses; the
       set agrees on one W; the ledger carries exactly one W line; the ledger agrees) are
       applied per leg, unchanged in logic.  The sixth (the value equals ONE typed
       constant) is replaced by a STRONGER one: the value must equal THAT LEG'S OWN
       registered window, drawn from a typed tuple, so the record cannot mislabel a leg.
  (N3) `--gscan` ADDS SEVEN REFUSALS THE PARENT CANNOT EXPRESS AT ALL, each driven with a
       control showing the parent ACCEPTS the same defect once relabelled: a missing `leg`
       key, an unregistered `leg`, a leg/W mislabel, a missing leg, an extra leg, a
       duplicated S5 inside a leg, and a per-leg ledger line that is absent, doubled or
       disagreeing.

ARM A IS STRUCTURALLY BARRED FROM `admissible: true`, AND THE BAR IS THREE-DEEP.
Arm A omits S2b, S3, S3b, S4 and S7, so it drops delta_repeat and delta_pert from
delta_eff.  delta_eff is a MAXIMUM, and removing a term from a maximum can only LOWER
h_min -- i.e. move toward `admissible: true`.  So Arm A may not size a step:
  BAR-1  `plan_gscan` never calls the parent's `g4_step_sizing`; the sizing entry point
         for gscan data is `_step_plan_refusal`, which raises.
  BAR-2  `main` REFUSES `--plan`/`--plan2`/`--plan3` on a gscan manifest, by detecting the
         multi-leg shape, before any gate runs.
  BAR-3  `_bar_admissible` walks the emitted object and REFUSES if any of `admissible`,
         `steps`, `h_min`, `h_star`, `step_plan` appears carrying anything but the
         registered refusal string.  BAR-3 is the one that survives a future edit: it
         catches a re-introduced step plan even if BAR-1 and BAR-2 are removed.

PLANTED CONTROLS RUN AT GRADE TIME, NOT ONLY IN THE SELFTEST (CLAUDE.md rule 3).
Every gate here that reads a number carries a live plant, and each plant is shown able to
FAIL IN A NAMED DIRECTION:
  GA-P1  the |g| reader is handed a synthetic row carrying PLANT_G and must return it;
         a reader that cannot see PLANT_G cannot report a magnitude.
  GA-P2  the window binding is handed a KNOWN-BAD three-leg set (A1 mislabelled as A0) and
         must REFUSE it; a binding not shown refusing is not a binding.
  GA-P3  the spend reader is handed a fixture ledger carrying PLANT_SPEND_CORE_MIN and
         must return it; a zero from a reader not shown able to see a non-zero is not
         evidence, and that zero would be read as headroom under the item ceiling.

NO `assert` STATEMENT APPEARS IN THIS FILE.  `python3 -O` deletes assert statements, and a
guard that disappears under an optimisation flag is not a guard.  `--assert-audit` counts
them by AST and must print 0; `--olimb` mutates this file and requires BOTH `python3` and
`python3 -O` to catch every mutant.

NOTHING HERE LAUNCHES ANYTHING.  This file reads artifacts and refuses; it starts no
container, writes into no run root it did not create, and authorises no compute.  The
pre-registration it serves (`W3S_PREREGISTRATION_DRAFT.md`) is UNFROZEN and this file is
NOT YET PINNED BY IT.  SUBMISSIONS REMAIN PARKED (CLAUDE.md rule 7).
"""
import argparse, hashlib, json, math, os, re, sys, tempfile

# ---------------------------------------------------------------- the parent, PINNED
PARENT_NAME = "d12y_grade_w3.py"
PARENT_MD5 = "3950d30fd09c9b56213a02f5e9864e20"

# ---------------------------------------------------------------- registered constants
# Arm A's three legs, ORDERED AND TYPED.  This tuple is the authority on which windows may
# appear in a gscan manifest; the parent expresses the same idea with ONE scalar constant
# and therefore cannot express a three-legged scan at all.
LEGS = (("A0", 2000), ("A1", 1400), ("A2", 3000))
LEG_NAMES = tuple(n for n, _ in LEGS)
LEG_W = dict(LEGS)
REGISTERED_WS = tuple(w for _, w in LEGS)

# FS-0, the gating control on the finding itself (W3S draft sec.4).
W_ANCHOR = 2000
G_ANCHOR = 0.48835975139977306
FS0_TOL_REL = 0.01

# The component the step is sized on.  INHERITED, not chosen here: the parent's `plan`
# reads `s5["dobj_dshape"][0]`, and the sweep S6_s{k} perturbs index 0, so the plateau and
# the sizing are on the same component.  It is NOT the largest component of this gradient
# and NOT the smallest; see the FINDING recorded in `--census-note`.
G_COMPONENT_INDEX = 0

# Inherited from the parent BY READING IT, and cross-checked against the value typed here.
# Typing it alone would drift; reading it alone would be a tautology (the file would agree
# with whatever the parent happened to say).  Both, and a refusal on disagreement.
C_ENV_EXPECTED = 0.8907
H_MAX_EXPECTED = 0.05
EPS_NOISE_TARGET_EXPECTED = 0.01

FS1_MARGIN = 1.15

# Prior measured windows, from roots on disk.  Their `step_plan.json` files predate W3-A1
# and W3-A2: they carry NO `W` key and NO `C_ENV`, so the WINDOW that produced each |g| is
# cross-read from that root's LEDGER, never from its step plan.  Absent artefact ->
# INFRASTRUCTURE (cross-read NOT MEASURED), the parent's own L-342 shape; disagreeing
# artefact -> REFUSAL.
PRIOR_LEGS = (
    (300, 1.0304158599180422,
     "/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady"),
    (900, 1.1398352621255485,
     "/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady"),
)

# ---- the cumulative item ceiling (T4).  LEG caps sum EXACTLY to the ceiling and the guard
# ---- REFUSES if they do not -- a registration whose parts exceed its whole is a defect
# ---- discovered here or not at all.
LEG_CAP_CORE_MIN = {"SETUP": 5.0, "A0": 100.0, "A1": 70.0, "A2": 155.0}
ITEM_CEILING_CORE_MIN = 330.0
CEILING_TOL_CORE_MIN = 0.02

# ---- rule-3 sentinels
PLANT_G = 1.234e-03
PLANT_SPEND_CORE_MIN = 12.345
PLANT_SPEND_TOL = 1.0e-9

GATES_EMITTED = ["GA-0", "GA-W", "GA-P1", "GA-P2", "GA-P3", "GA-1", "GA-2", "GA-3",
                 "GA-BAR", "GA-CEIL"]

# BAR-3's key set and the ONLY value any of them may carry in a gscan artefact.
BARRED_KEYS = ("admissible", "steps", "h_min", "h_star", "step_plan", "h_star_wrong")
BAR_REFUSAL_STRING = ("REFUSED: Arm A drops delta_repeat and delta_pert from delta_eff and "
                      "therefore CANNOT size a step (W3S draft sec.3.1)")


class Refusal(Exception):
    pass


class SelfTestFailure(Exception):
    pass


def check(cond, msg="unit check failed"):
    """The `assert` replacement.  `python3 -O` deletes `assert`; it does not delete this."""
    if not cond:
        raise SelfTestFailure(msg)


def _finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x))


def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


_PARENT_CACHE = []


def parent():
    """Import the FROZEN parent after checking its md5.  A pin that is not checked is a
    comment.  The parent is imported, never copied: a copied gate drifts silently."""
    if _PARENT_CACHE:
        return _PARENT_CACHE[0]
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), PARENT_NAME)
    if not os.path.isfile(p):
        raise Refusal("the frozen parent %s is not on disk beside this file" % PARENT_NAME)
    got = _md5(p)
    if got != PARENT_MD5:
        raise Refusal("FROZEN PARENT DRIFTED: %s md5 %s, pinned %s. CLAUDE.md rule 6 says a "
                      "frozen file is never edited; this successor refuses rather than "
                      "grading against an instrument that is not the one it was written "
                      "against." % (PARENT_NAME, got, PARENT_MD5))
    import importlib.util
    spec = importlib.util.spec_from_file_location("_d12y_grade_w3_frozen", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # ---- the inherited numbers are READ, then cross-checked against the typed ones.
    for name, want in (("C_ENV", C_ENV_EXPECTED), ("H_MAX", H_MAX_EXPECTED),
                       ("EPS_NOISE_TARGET", EPS_NOISE_TARGET_EXPECTED)):
        have = getattr(mod, name, None)
        if not _finite(have) or abs(float(have) - want) > 1e-12:
            raise Refusal("inherited constant %s is %r in the parent, %r here -- this "
                          "successor will not grade on a constant it and its parent "
                          "disagree about" % (name, have, want))
    _PARENT_CACHE.append(mod)
    return mod


def wg_required():
    """h_min = 100*C_ENV/(W*|g|); admissible needs h_min <= h_max, i.e. W*|g| >= this.
    DERIVED from the inherited constants at call time, never typed as a product."""
    p = parent()
    return (p.C_ENV / p.EPS_NOISE_TARGET) / p.H_MAX


def fs1_bar():
    return wg_required() * FS1_MARGIN


# ==================================================================================
# THE `--gscan` WINDOW BINDING.  This is the clause the supervisor reads AS A DIFF;
# `w3s_grade_NARROWING.diff` is that diff, and `--selftest-narrowing` drives it.
# ==================================================================================
def _leg_ledger_re(leg):
    return re.compile(r"^W_STEPS_%s=(\d+)\b" % re.escape(leg))


def _w_from_record_gscan(rows, ledger_path, infra=None):
    """W3S-A1.  THE GSCAN BINDING.  Returns {leg: W} -- a DICT, never the parent's scalar,
    so a caller written against the parent's return type cannot silently consume this one.

    LIMB BY LIMB, against the parent's `_w_from_record` (d12y_grade_w3.py:2101-2160):

      parent L1  every row carries `W`                 -> KEPT, whole manifest
      parent L2  every `W` parses as int               -> KEPT, whole manifest
      parent L3  the rows agree on ONE `W`             -> KEPT PER LEG, and REPLACED at the
                                                          manifest level by the leg-set
                                                          closure below, which enumerates
                                                          the permitted windows instead of
                                                          merely requiring one of them
      parent L4  ledger carries exactly one W line     -> KEPT PER LEG (one per leg, three)
      parent L5  the ledger agrees with the rows       -> KEPT PER LEG
      parent L6  the value IS the one typed constant   -> STRENGTHENED: the value must be
                                                          THAT LEG'S registered window,
                                                          from a typed tuple, so a row
                                                          cannot sit under the wrong leg

    NEW LIMBS THE PARENT CANNOT EXPRESS (each driven in `--selftest-narrowing` with a
    control showing the parent ACCEPTS the same defect once relabelled):
      N1 every row carries a `leg` key
      N2 every `leg` is one of the registered leg names
      N3 the row's `W` equals its own leg's registered window   (the mislabel limb)
      N4 the leg set is EXACTLY the registered leg set          (no missing, no extra)
      N5 the registered legs carry DISTINCT windows             (registration self-check)
      N6 exactly one S5 row per leg                             (a re-fired stage is a
                                                                 FINDING, W3-A3's shape)
      N7 the ledger's per-leg W lines, absent / doubled / disagreeing
    """
    if not rows:
        raise Refusal("W3S-A1: no manifest rows -- an empty set is not a scan")

    # ---- N5.  REGISTRATION SELF-CHECK, before any datum is read.  Two legs sharing a
    # window would make the scan degenerate while every data limb below still passed.
    if len(set(REGISTERED_WS)) != len(REGISTERED_WS):
        raise Refusal("W3S-A1 N5: the registered legs do not carry distinct windows: %r. A "
                      "scan whose legs share a window measures one point twice."
                      % (LEGS,))
    if len(set(LEG_NAMES)) != len(LEG_NAMES):
        raise Refusal("W3S-A1 N5: duplicate leg name in the registered legs: %r" % (LEGS,))

    # ---- parent L1, verbatim in intent and in message shape.
    missing = [r.get("name") for r in rows if "W" not in r]
    if missing:
        raise Refusal("W3S-A1: %d manifest row(s) carry no W key: %s"
                      % (len(missing), missing[:6]))
    # ---- N1.
    missing_leg = [r.get("name") for r in rows if "leg" not in r]
    if missing_leg:
        raise Refusal("W3S-A1 N1: %d manifest row(s) carry no `leg` key: %s. The parent "
                      "never reads `leg` and would accept these rows once they agreed on "
                      "W; a gscan row that cannot say which leg it belongs to cannot be "
                      "graded against that leg's registered window."
                      % (len(missing_leg), missing_leg[:6]))
    # ---- parent L2.
    for r in rows:
        try:
            int(r["W"])
        except (TypeError, ValueError):
            raise Refusal("W3S-A1: row %r carries an unparseable W=%r"
                          % (r.get("name"), r.get("W")))
    # ---- N2.
    bad_leg = sorted({str(r.get("leg")) for r in rows if r.get("leg") not in LEG_NAMES})
    if bad_leg:
        raise Refusal("W3S-A1 N2: unregistered leg name(s) %s; the registered legs are %s"
                      % (bad_leg, list(LEG_NAMES)))

    part = {}
    for r in rows:
        part.setdefault(r["leg"], []).append(r)

    # ---- N4.  THE LEG-SET CLOSURE.  This is the limb that makes the binding a NARROWING
    # rather than a relaxation: it does not merely permit several windows, it ENUMERATES
    # the exact multiset of legs the pre-registration bought, so a manifest that is short
    # a leg -- or carries one it did not register -- refuses.  It is also why every
    # window-homogeneous manifest, INCLUDING every manifest the parent ACCEPTS, refuses
    # here: a single-window manifest is missing two of the three registered legs.
    if set(part) != set(LEG_NAMES):
        raise Refusal("W3S-A1 N4: the manifest's leg set %s is not the registered leg set "
                      "%s. Missing: %s. Extra: %s."
                      % (sorted(part), list(LEG_NAMES),
                         sorted(set(LEG_NAMES) - set(part)), sorted(set(part) - set(LEG_NAMES))))

    ledger_present = os.path.isfile(ledger_path)
    led_lines = []
    if ledger_present:
        with open(ledger_path, errors="replace") as f:
            led_lines = list(f)

    out = {}
    for leg in LEG_NAMES:
        lrows = part.get(leg)
        if not lrows:
            raise Refusal("W3S-A1 N4: leg %s partitioned to ZERO rows" % leg)
        # ---- parent L3, PER LEG.
        ws = set()
        for r in lrows:
            ws.add(int(r["W"]))
        if len(ws) != 1:
            raise Refusal("W3S-A1: leg %s's manifest rows disagree on W: %s"
                          % (leg, sorted(ws)))
        w = ws.pop()
        # ---- N3 / parent L6 STRENGTHENED.
        if w != LEG_W[leg]:
            raise Refusal("W3S-A1 N3: leg %s carries W=%d, its registered window is %d. The "
                          "parent's single W_PRIMARY constant cannot say which leg a window "
                          "belongs to; this limb can, and a mislabelled leg is the "
                          "W2R-GRADER-DEF-1 defect wearing a leg name."
                          % (leg, w, LEG_W[leg]))
        # ---- N6.  Exactly one S5 per leg.  A second S5 in one leg is a re-fired stage --
        # a FINDING, never something for a comparator to pick between (W3-A3's reasoning).
        s5s = [r for r in lrows if r.get("name") == "S5"]
        if len(s5s) != 1:
            raise Refusal("W3S-A1 N6: leg %s carries %d rows named S5, expected exactly 1. "
                          "A second adjoint row in one leg is a re-fired stage: a FINDING, "
                          "not something to resolve by sort order." % (leg, len(s5s)))
        # ---- parent L4/L5 PER LEG (N7), with the parent's own absent-ledger reasoning.
        if not ledger_present:
            continue
        rx = _leg_ledger_re(leg)
        led = [int(m.group(1)) for m in (rx.match(ln.strip()) for ln in led_lines) if m]
        if len(led) != 1:
            raise Refusal("W3S-A1 N7: the ledger carries %d W_STEPS_%s= line(s), expected "
                          "exactly 1: %s. A record that is present and AMBIGUOUS is not a "
                          "record." % (len(led), leg, led))
        if led[0] != w:
            raise Refusal("W3S-A1 N7: ledger W_STEPS_%s=%d disagrees with leg %s's manifest "
                          "rows' W=%d (the W2R-GRADER-DEF-1 defect shape)"
                          % (leg, led[0], leg, w))
        out[leg] = w

    if not ledger_present:
        # The parent's own branch, reproduced in its own reasoning: the ledger is a
        # host-side `tee -a` written by the launcher, so its ABSENCE is a BOOKKEEPING
        # failure (L-342). THE WINDOWS ARE NOT WAIVED -- N1..N4 and N3's registered-window
        # pin all ran above against constants this file types, ledger or no ledger. What
        # is lost is only the CROSS-READ.
        note = ("W3S-A1: ledger absent at %s -- the manifest<->ledger per-leg W CROSS-READ "
                "is NOT MEASURED (INFRASTRUCTURE, L-342). The windows are NOT waived: every "
                "row carries W and `leg`, every leg is registered, the leg set is exactly "
                "%s, and each leg's W was checked against its own registered window. "
                "Corroboration lost; the values stand." % (ledger_path, list(LEG_NAMES)))
        if infra is not None:
            infra.append(note)
        else:
            sys.stderr.write("INFRASTRUCTURE DEFECT (reported, not fatal): %s\n" % note)
        out = dict(LEG_W)

    if set(out) != set(LEG_NAMES):
        raise Refusal("W3S-A1: internal -- the binding returned legs %s, not %s"
                      % (sorted(out), list(LEG_NAMES)))
    return out


# ==================================================================================
# BAR-3.  THE STRUCTURAL BAR ON `admissible`.
# ==================================================================================
def _bar_admissible(obj, where="gscan artefact"):
    """BAR-3.  Walk the object about to be emitted and REFUSE if it carries a step plan.

    This is the limb that survives a future edit.  BAR-1 (never calling the sizing
    function) and BAR-2 (refusing --plan on gscan data) are both single lines somebody
    could delete; this one sees the RESULT of deleting them, because a re-introduced step
    plan has to travel through the emitted object to reach a reader.
    """
    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in BARRED_KEYS and v != BAR_REFUSAL_STRING:
                    raise Refusal(
                        "GA-BAR: the %s carries %r at %s = %r. ARM A DROPS delta_repeat AND "
                        "delta_pert FROM delta_eff, and delta_eff is a MAXIMUM -- removing a "
                        "term from a maximum can only LOWER h_min, i.e. move toward "
                        "`admissible: true`. Arm A therefore may not size a step, and an "
                        "artefact that carries one is refused rather than published."
                        % (where, k, path + "/" + str(k), v))
                walk(v, path + "/" + str(k))
        elif isinstance(o, (list, tuple)):
            for i, v in enumerate(o):
                walk(v, path + "[%d]" % i)
    walk(obj, "")
    return {"gate": "GA-BAR", "verdict": "PASS",
            "barred_keys": list(BARRED_KEYS),
            "note": "no step plan reached the emitted artefact"}


def _step_plan_refusal(*_a, **_k):
    """BAR-1.  The sizing entry point for gscan data.  It raises, always."""
    raise Refusal("GA-BAR / BAR-1: a step plan was requested from `--gscan` data. Arm A "
                  "omits S2b, S3, S3b, S4 and S7, so delta_repeat and delta_pert are NOT "
                  "MEASURED and delta_eff cannot be formed. " + BAR_REFUSAL_STRING)


# ==================================================================================
# THE NUMBER-READING GATES, EACH WITH ITS LIVE PLANT
# ==================================================================================
def read_g(rows, leg, index=G_COMPONENT_INDEX):
    """Read |g| for one leg from that leg's S5 row.  REFUSES rather than returning zero."""
    s5 = [r for r in rows if r.get("leg") == leg and r.get("name") == "S5"]
    if len(s5) != 1:
        raise Refusal("GA-1: leg %s has %d S5 rows; |g| cannot be read" % (leg, len(s5)))
    v = s5[0].get("dobj_dshape")
    if not isinstance(v, (list, tuple)) or len(v) == 0:
        raise Refusal("GA-1: leg %s's S5 row carries no dobj_dshape vector -- a reader that "
                      "read nothing has not measured zero" % leg)
    if index >= len(v):
        raise Refusal("GA-1: leg %s's gradient has %d components, the registered sizing "
                      "component is index %d" % (leg, len(v), index))
    g = v[index]
    if not _finite(g):
        raise Refusal("GA-1: leg %s's g[%d] = %r is not finite" % (leg, index, g))
    if float(g) == 0.0:
        raise Refusal("GA-1: leg %s's g[%d] is EXACTLY ZERO. h_min divides by |g|; a zero "
                      "here is not a small gradient, it is a reader or a solve that "
                      "produced nothing (CLAUDE.md rule 3)." % (leg, index))
    return abs(float(g))


def ga_p1_plant_g():
    """GA-P1.  The |g| reader is shown able to SEE a planted non-zero, and shown REFUSING
    the two zero-shaped inputs it must never report as a magnitude."""
    vec = [0.0] * (G_COMPONENT_INDEX + 1)
    vec[G_COMPONENT_INDEX] = PLANT_G
    planted = [{"name": "S5", "leg": LEG_NAMES[0], "W": LEG_W[LEG_NAMES[0]],
                "dobj_dshape": vec}]
    got = read_g(planted, LEG_NAMES[0])
    if abs(got - PLANT_G) > 1e-15:
        raise Refusal("GA-P1 REFUSAL: the |g| reader was handed a planted g[%d]=%g and "
                      "returned %r. A READER THAT CANNOT SEE A NON-ZERO CANNOT REPORT A "
                      "MAGNITUDE (CLAUDE.md rule 3)." % (G_COMPONENT_INDEX, PLANT_G, got))
    # the two named failure directions, DRIVEN
    seen = []
    for label, vec2 in (("all-zero gradient", [0.0] * (G_COMPONENT_INDEX + 1)),
                        ("absent gradient vector", None)):
        row = {"name": "S5", "leg": LEG_NAMES[0], "W": LEG_W[LEG_NAMES[0]]}
        if vec2 is not None:
            row["dobj_dshape"] = vec2
        try:
            read_g([row], LEG_NAMES[0])
        except Refusal:
            seen.append(label)
    if len(seen) != 2:
        raise Refusal("GA-P1 REFUSAL: the |g| reader FAILED TO REFUSE %s. A control never "
                      "shown failing is not a control."
                      % (sorted({"all-zero gradient", "absent gradient vector"} - set(seen))))
    return {"gate": "GA-P1", "verdict": "PASS", "plant": PLANT_G, "read_back": got,
            "refused_directions": seen,
            "note": "the |g| reader saw a planted non-zero AND refused both zero shapes"}


def ga_p2_plant_binding(tmpdir):
    """GA-P2.  The window binding is handed a KNOWN-BAD three-leg set and must REFUSE it,
    and the matching CLEAN set and must ACCEPT it.  Both directions, at grade time."""
    def rows_for(mislabel):
        rs = []
        for leg in LEG_NAMES:
            w = LEG_W[leg]
            if mislabel and leg == "A1":
                rs.append({"name": "S5", "leg": "A0", "W": w, "dobj_dshape": [1.0]})
            else:
                rs.append({"name": "S5", "leg": leg, "W": w, "dobj_dshape": [1.0]})
        return rs
    d = tempfile.mkdtemp(dir=tmpdir, prefix="ga_p2_")
    lp = os.path.join(d, "ledger.txt")
    with open(lp, "w") as f:
        f.write("\n".join("W_STEPS_%s=%d" % (n, LEG_W[n]) for n in LEG_NAMES) + "\n")
    clean_ok = True
    try:
        _w_from_record_gscan(rows_for(False), lp, infra=[])
    except Refusal:
        clean_ok = False
    bad_refused = False
    try:
        _w_from_record_gscan(rows_for(True), lp, infra=[])
    except Refusal:
        bad_refused = True
    if not clean_ok:
        raise Refusal("GA-P2 REFUSAL: the window binding REFUSED its own clean control. A "
                      "binding that refuses everything has not been shown to bind anything.")
    if not bad_refused:
        raise Refusal("GA-P2 REFUSAL: the window binding ACCEPTED a planted leg mislabel "
                      "(leg A1's rows filed under leg A0). A binding not shown REFUSING is "
                      "not a binding (CLAUDE.md rule 3, L-314).")
    return {"gate": "GA-P2", "verdict": "PASS",
            "note": "the binding accepted the clean three-leg set and REFUSED a planted "
                    "leg mislabel; both directions driven at grade time"}


def ga_1_magnitudes(rows, legs_w):
    per = {}
    for leg in LEG_NAMES:
        g = read_g(rows, leg)
        w = legs_w[leg]
        per[leg] = {"W": w, "abs_g": g, "W_times_abs_g": w * g}
    return {"gate": "GA-1", "verdict": "PASS", "component_index": G_COMPONENT_INDEX,
            "per_leg": per}


def ga_2_fs0(per_leg):
    """FS-0, the GATING control on the finding itself.  Leg A0 re-measures |g(2000)| in a
    fresh root; outside +/-1 % the whole item's reasoning was a single-sample artefact."""
    anchor_leg = [n for n, w in LEGS if w == W_ANCHOR]
    if len(anchor_leg) != 1:
        raise Refusal("GA-2: %d registered legs carry the anchor window %d; FS-0 needs "
                      "exactly one" % (len(anchor_leg), W_ANCHOR))
    leg = anchor_leg[0]
    got = per_leg[leg]["abs_g"]
    rel = abs(got - abs(G_ANCHOR)) / abs(G_ANCHOR)
    hit = rel <= FS0_TOL_REL
    return {"gate": "GA-2", "falsifier": "FS-0", "leg": leg,
            "verdict": "PASS" if hit else "NOT A RESULT",
            "outcome": "HIT" if hit else "MISS",
            "abs_g_measured": got, "abs_g_registered": abs(G_ANCHOR),
            "rel_deviation": rel, "tol_rel": FS0_TOL_REL,
            "note": ("leg %s reproduced the anchor within the registered band" % leg) if hit
                    else ("leg %s did NOT reproduce |g(%d)|; RESULTS_W3.md sec.6.5's W*|g| "
                          "reading is a SINGLE-SAMPLE artefact and the arm STOPS here"
                          % (leg, W_ANCHOR))}


def ga_3_fs1(per_leg, priors):
    """FS-1.  Does ANY measured window clear the margined requirement?"""
    bar = fs1_bar()
    pts = []
    for w, g, src in priors:
        pts.append({"W": w, "abs_g": g, "W_times_abs_g": w * g, "source": src,
                    "provenance": "PRIOR (registered)"})
    for leg in LEG_NAMES:
        d = per_leg[leg]
        pts.append({"W": d["W"], "abs_g": d["abs_g"], "W_times_abs_g": d["W_times_abs_g"],
                    "source": "leg %s, this run" % leg, "provenance": "ARM A"})
    clearing = sorted([p for p in pts if p["W_times_abs_g"] >= bar], key=lambda p: p["W"])
    hit = bool(clearing)
    return {"gate": "GA-3", "falsifier": "FS-1",
            "verdict": "PASS" if hit else "NOT A RESULT",
            "outcome": "HIT" if hit else "MISS",
            "requirement_unmargined": wg_required(), "margin": FS1_MARGIN, "bar": bar,
            "points": sorted(pts, key=lambda p: p["W"]),
            "max_W_times_abs_g": max(p["W_times_abs_g"] for p in pts),
            "W_adm": clearing[0]["W"] if hit else None,
            "arm_b_fires": hit,
            "note": ("Arm B fires at the SMALLEST clearing window" if hit else
                     "no window in the measured set clears the margined bar; ARM B LAUNCHES "
                     "NOTHING. Scoped to the MEASURED SET -- this says nothing about W > %d."
                     % max(p["W"] for p in pts))}


def read_priors(infra):
    """Cross-read each prior's window from that root's LEDGER, never from its step plan:
    the prior roots predate W3-A2 and their step plans carry no W key at all."""
    out = []
    for w, g, root in PRIOR_LEGS:
        led = os.path.join(root, "ledger.txt")
        if not os.path.isfile(led):
            infra.append("GA-3: prior W=%d -- ledger absent at %s, the window CROSS-READ is "
                         "NOT MEASURED (INFRASTRUCTURE, L-342); the registered value stands."
                         % (w, led))
            out.append((w, g, root + " (cross-read NOT MEASURED)"))
            continue
        seen = []
        with open(led, errors="replace") as f:
            for line in f:
                m = re.match(r"^W_STEPS=(\d+)\b", line.strip())
                if m:
                    seen.append(int(m.group(1)))
        if len(seen) != 1:
            raise Refusal("GA-3: prior root %s carries %d W_STEPS= ledger line(s), expected "
                          "exactly 1: %s" % (root, len(seen), seen))
        if seen[0] != w:
            raise Refusal("GA-3: prior root %s ran at W=%d, the registered prior says W=%d. "
                          "A prior whose window cannot be corroborated is not a prior."
                          % (root, seen[0], w))
        out.append((w, g, led))
    return out


# ==================================================================================
# T4.  THE CUMULATIVE ITEM-CEILING GUARD.  Union of d6rf_chain_driver.sh:164-169
#      (the comparison and `exit 6`) and a1wrt_run_unit.sh:283-317 (the UNMEASURED
#      refusal limb, which d6rf lacks), plus three limbs neither has.
# ==================================================================================
SPEND_LINE_RE = re.compile(r"^(?:STAGE|ARM|LEG)=")
# THE TOKEN IS CAPTURED WHOLE AND THEN VALIDATED WHOLE.  d6rf's `[0-9.]+` -- and this
# file's own first draft -- match `1.2` out of a malformed `core_min=1.2.3` and return a
# WRONG NUMBER SILENTLY; d6rf then loses the ValueError entirely (its `except IOError`
# does not catch it), `$SPENT` comes back EMPTY, its projection comparison fails, and the
# guard FAILS OPEN.  So: take everything up to whitespace, and require the WHOLE token to
# be a plain non-negative decimal.  Anything else is UNMEASURED, never a number.
CORE_MIN_RE = re.compile(r"\bcore_min=(\S*)")
CORE_MIN_VALUE_RE = re.compile(r"^[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$")


def spend_from_root(root):
    """Return (core_min, note).  core_min is None meaning UNMEASURED -- never 0.0.

    d6rf reads the ledger and sums; if it cannot parse, awk yields 0 and the ceiling check
    silently sees full headroom.  a1wrt adds the UNMEASURED limb but reads a MISSING ledger
    as 0.0 unconditionally.  THIS ADDS THE THIRD CASE NEITHER HAS: a run root that EXISTS
    and carries stage logs but has NO ledger has spent money nobody can count, and that is
    UNMEASURED, not zero.  A zero that means "could not read" is a planted zero.
    """
    led = os.path.join(root, "ledger.txt")
    root_exists = os.path.isdir(root)
    if not root_exists and not os.path.exists(led):
        return 0.0, "FRESH: neither the root nor its ledger exists"
    if not os.path.isfile(led):
        stage_logs = []
        if root_exists:
            stage_logs = [p for p in os.listdir(root) if p.endswith(".log")]
        return None, ("UNMEASURED: the root %s EXISTS and carries %d .log file(s) but has no "
                      "ledger.txt. Spend that happened and was not recorded is UNMEASURED, "
                      "not zero." % (root, len(stage_logs)))
    tot = 0.0
    cands = 0
    unparsed = []
    try:
        with open(led, errors="replace") as f:
            for ln in f:
                s = ln.strip()
                if not SPEND_LINE_RE.match(s):
                    continue
                cands += 1
                m = CORE_MIN_RE.search(s)
                if not m:
                    unparsed.append(s[:80])
                    continue
                tok = m.group(1)
                if not CORE_MIN_VALUE_RE.match(tok):
                    unparsed.append(s[:80])
                    continue
                v = float(tok)
                if not math.isfinite(v) or v < 0.0:
                    unparsed.append(s[:80])
                    continue
                tot += v
    except (IOError, OSError, ValueError):
        return None, "UNMEASURED: %s exists but could not be read or parsed" % led
    if unparsed:
        return None, ("UNMEASURED: %d spend-shaped ledger line(s) in %s carry no parseable "
                      "core_min=: %s. An unknown prior spend cannot be shown to fit under "
                      "the ceiling, so this refuses rather than assuming zero."
                      % (len(unparsed), led, unparsed[:2]))
    if cands == 0:
        logs = [p for p in os.listdir(root) if p.endswith(".log")] if root_exists else []
        if logs:
            return None, ("UNMEASURED: %s carries ZERO spend-shaped lines while the root "
                          "holds %d .log file(s). Stages ran and the ledger did not record "
                          "them." % (led, len(logs)))
        return 0.0, "FRESH: ledger present, no stage has run yet"
    return tot, "MEASURED from %d ledger row(s) in %s" % (cands, led)


def ga_p3_plant_spend(tmpdir):
    """GA-P3.  The spend reader is shown able to SEE a planted non-zero, and shown REFUSING
    an unparseable ledger.  Without this, a reader that returns 0.0 because it broke is
    indistinguishable from a fresh root -- and 0.0 reads as full headroom."""
    d = tempfile.mkdtemp(dir=tmpdir, prefix="ga_p3_")
    good = os.path.join(d, "good")
    os.makedirs(good)
    with open(os.path.join(good, "ledger.txt"), "w") as f:
        f.write("ITEM=W3S\nSTAGE=S5 TASK=compute_totals rc=0 wall_s=10 ranks=1 "
                "core_min=%s memavail_GiB=20.0\n" % PLANT_SPEND_CORE_MIN)
    got, note = spend_from_root(good)
    if got is None or abs(got - PLANT_SPEND_CORE_MIN) > PLANT_SPEND_TOL:
        raise Refusal("GA-P3 REFUSAL: the spend reader was handed a planted "
                      "core_min=%s and returned %r (%s). A READER THAT CANNOT SEE A "
                      "NON-ZERO CANNOT REPORT A ZERO, and this zero would be read as "
                      "headroom under the item ceiling (CLAUDE.md rule 3)."
                      % (PLANT_SPEND_CORE_MIN, got, note))
    directions = []
    bad = os.path.join(d, "bad")
    os.makedirs(bad)
    with open(os.path.join(bad, "ledger.txt"), "w") as f:
        f.write("STAGE=S5 TASK=compute_totals rc=0 wall_s=10 ranks=1 memavail_GiB=20.0\n")
    if spend_from_root(bad)[0] is None:
        directions.append("spend-shaped line with no core_min= -> UNMEASURED")
    noled = os.path.join(d, "noledger")
    os.makedirs(noled)
    open(os.path.join(noled, "S5_x.log"), "w").write("x\n")
    if spend_from_root(noled)[0] is None:
        directions.append("root with stage logs and no ledger -> UNMEASURED")
    empty = os.path.join(d, "emptyled")
    os.makedirs(empty)
    open(os.path.join(empty, "S5_x.log"), "w").write("x\n")
    open(os.path.join(empty, "ledger.txt"), "w").write("ITEM=W3S\n")
    if spend_from_root(empty)[0] is None:
        directions.append("ledger with zero spend rows beside stage logs -> UNMEASURED")
    if len(directions) != 3:
        raise Refusal("GA-P3 REFUSAL: the spend reader failed to return UNMEASURED in one "
                      "of its three named directions; only %r fired. A control never shown "
                      "failing is not a control." % (directions,))
    return {"gate": "GA-P3", "verdict": "PASS", "plant": PLANT_SPEND_CORE_MIN,
            "read_back": got, "refused_directions": directions}


def cumulative_item_ceiling_census(leg, roots, tmpdir):
    """GA-CEIL.  The cumulative item ceiling, asserted BEFORE the leg runs.

    Return codes are the caller's contract:
      0   OK to proceed
      6   CEILING or ALREADY_BOUGHT   (d6rf's exit 6)
      64  REGISTRATION INCONSISTENT   (the caps do not fit the ceiling)
      65  UNMEASURED prior spend      (a1wrt's exit 65)
    """
    if leg not in LEG_CAP_CORE_MIN:
        return 64, {"gate": "GA-CEIL", "verdict": "BLOCKED",
                    "reason": "no registered cap for leg %r; the registered legs are %s"
                              % (leg, sorted(LEG_CAP_CORE_MIN))}
    total_caps = sum(LEG_CAP_CORE_MIN.values())
    if total_caps > ITEM_CEILING_CORE_MIN + CEILING_TOL_CORE_MIN:
        return 64, {"gate": "GA-CEIL", "verdict": "BLOCKED",
                    "reason": "REGISTRATION INCONSISTENT: the leg caps sum to %.3f, above "
                              "the registered item ceiling %.3f. A registration whose parts "
                              "exceed its whole is a defect found here or not at all."
                              % (total_caps, ITEM_CEILING_CORE_MIN)}
    plant = ga_p3_plant_spend(tmpdir)
    spent = 0.0
    notes = []
    for root in roots:
        v, note = spend_from_root(root)
        notes.append({"root": root, "core_min": v, "note": note})
        if v is None:
            return 65, {"gate": "GA-CEIL", "verdict": "BLOCKED", "plant": plant,
                        "roots": notes,
                        "reason": "ABORT ITEM CEILING: prior spend is UNMEASURED. %s An "
                                  "unknown prior spend plus this leg's %.1f core-min cap "
                                  "cannot be shown to fit under the %.1f ceiling, so this "
                                  "refuses rather than assuming zero."
                                  % (note, LEG_CAP_CORE_MIN[leg], ITEM_CEILING_CORE_MIN)}
        spent += v
        # ---- d6rf's ALREADY_BOUGHT: a second record for one run is the defect.
        led = os.path.join(root, "ledger.txt")
        if os.path.isfile(led):
            with open(led, errors="replace") as f:
                for ln in f:
                    if re.match(r"^LEG=%s\b.*\brc=0\b" % re.escape(leg), ln.strip()):
                        return 6, {"gate": "GA-CEIL", "verdict": "BLOCKED", "plant": plant,
                                   "roots": notes,
                                   "reason": "ABORT ALREADY_BOUGHT: leg %s already has an "
                                             "rc=0 ledger row in %s; a second record for "
                                             "one run is the defect." % (leg, led)}
    cap = LEG_CAP_CORE_MIN[leg]
    proj = spent + cap
    body = {"gate": "GA-CEIL", "leg": leg, "plant": plant, "roots": notes,
            "spent_core_min": spent, "leg_cap_core_min": cap,
            "projected_worst_case": proj,
            "item_ceiling_core_min": ITEM_CEILING_CORE_MIN,
            "registered_leg_caps": dict(LEG_CAP_CORE_MIN),
            "leg_caps_sum": total_caps}
    if proj > ITEM_CEILING_CORE_MIN + CEILING_TOL_CORE_MIN:
        body["verdict"] = "BLOCKED"
        body["reason"] = ("ABORT ITEM CEILING: %.3f core-min already spent + this leg's %.1f "
                          "cap = %.3f > the registered ceiling %.1f. An overrun STOPS the "
                          "run; it does not get a new budget (CLAUDE.md rule 12)."
                          % (spent, cap, proj, ITEM_CEILING_CORE_MIN))
        return 6, body
    body["verdict"] = "PASS"
    body["reason"] = ("spent %.3f + leg cap %.1f = %.3f <= ceiling %.1f"
                      % (spent, cap, proj, ITEM_CEILING_CORE_MIN))
    return 0, body


# ==================================================================================
# THE GSCAN GRADE
# ==================================================================================
def _read_manifest_rows(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        raise Refusal("manifest %s holds NO stage rows" % path)
    return rows


def looks_like_gscan(rows):
    """BAR-2's detector.  A gscan manifest is one carrying more than one distinct W, or any
    `leg` key at all.  Used to refuse a step-plan request, never to grant one."""
    ws = {r.get("W") for r in rows}
    return len(ws) > 1 or any("leg" in r for r in rows)


def plan_gscan(manifest_path, root, tmpdir="/tmp"):
    """`--gscan`.  Arm A's diagnostic.  Grades NO admissibility and sizes NO step."""
    p = parent()
    rows = [r for r in _read_manifest_rows(manifest_path) if not r.get("blocked")]
    infra = []
    out = {"gates": [], "infrastructure_defects": infra,
           "parent": {"file": PARENT_NAME, "md5": PARENT_MD5, "edited": False},
           "registered": {"legs": [list(x) for x in LEGS],
                          "anchor_W": W_ANCHOR, "anchor_abs_g": abs(G_ANCHOR),
                          "fs0_tol_rel": FS0_TOL_REL,
                          "requirement_unmargined": wg_required(),
                          "fs1_margin": FS1_MARGIN, "fs1_bar": fs1_bar(),
                          "C_ENV": p.C_ENV, "h_max": p.H_MAX,
                          "eps_noise_target": p.EPS_NOISE_TARGET,
                          "component_index": G_COMPONENT_INDEX}}

    # ---- GA-0: completion, delegated to the FROZEN parent's own gate, uncopied.
    out["gates"].append(p.g0_completion(rows))
    # ---- the live plants, BEFORE any number is used.
    out["gates"].append(ga_p1_plant_g())
    out["gates"].append(ga_p2_plant_binding(tmpdir))
    # ---- GA-W: the narrowed window binding.
    legs_w = _w_from_record_gscan(rows, os.path.join(root, "ledger.txt"), infra=infra)
    out["gates"].append({"gate": "GA-W", "verdict": "PASS", "legs": legs_w,
                         "binding": "W3S-A1 (--gscan), strictly narrower than the parent's "
                                    "_w_from_record; see w3s_grade_NARROWING.diff"})
    # ---- GA-1 / GA-2 / GA-3
    g1 = ga_1_magnitudes(rows, legs_w)
    out["gates"].append(g1)
    g2 = ga_2_fs0(g1["per_leg"])
    out["gates"].append(g2)
    priors = read_priors(infra)
    g3 = ga_3_fs1(g1["per_leg"], priors)
    out["gates"].append(g3)

    # ---- the verdict, from the fixed vocabulary only (CLAUDE.md rule 1).
    if g2["outcome"] == "MISS":
        verdict, why = "NOT A RESULT", "FS-0 MISS: the anchor did not reproduce"
    elif g3["outcome"] == "MISS":
        verdict, why = ("NOT A RESULT",
                        "FS-0 HIT, FS-1 MISS: no measured window clears the margined "
                        "requirement; Arm B launches nothing")
    else:
        verdict, why = ("PENDING",
                        "FS-0 HIT, FS-1 HIT at W_adm=%r: Arm B is registered to fire and "
                        "has not run" % g3["W_adm"])
    out["arm_a_verdict"] = verdict
    out["arm_a_verdict_reason"] = why
    out["arm_b_fires"] = bool(g3["arm_b_fires"])
    out["W_adm"] = g3["W_adm"]
    out["step_plan"] = BAR_REFUSAL_STRING
    out["admissible"] = BAR_REFUSAL_STRING
    out["n_infrastructure_defects"] = len(infra)

    # ---- BAR-3, LAST, on the object about to be written.
    out["gates"].append(_bar_admissible(out, where="gscan_plan.json"))
    with open(os.path.join(root, "gscan_plan.json"), "w") as f:
        json.dump(out, f, indent=2, sort_keys=True, default=str)
    return out


# ==================================================================================
# SELFTESTS
# ==================================================================================
def _mkledger(tmpdir, lines):
    d = tempfile.mkdtemp(dir=tmpdir, prefix="led_")
    lp = os.path.join(d, "ledger.txt")
    with open(lp, "w") as f:
        f.write("\n".join(lines) + "\n")
    return lp


def _clean_gscan_rows():
    rs = []
    for leg in LEG_NAMES:
        rs.append({"name": "S5", "leg": leg, "W": LEG_W[leg], "dobj_dshape": [1.0, 2.0]})
        rs.append({"name": "S2a", "leg": leg, "W": LEG_W[leg]})
    return rs


def _clean_gscan_ledger_lines():
    return ["ITEM=W3S"] + ["W_STEPS_%s=%d" % (n, LEG_W[n]) for n in LEG_NAMES]


def selftest_narrowing(tmpdir):
    """THE NARROWING PROOF, DRIVEN AGAINST THE PARENT'S OWN FUNCTION -- both directions.

    Nothing here is asserted in prose. Every leg builds an input, runs BOTH gates on it,
    and records which refused. The parent is the FROZEN file on disk, imported after its
    md5 is checked, so this cannot drift out of agreement with the thing it cites.
    """
    p = parent()
    n = 0
    bad = []

    def unit(name, cond):
        nonlocal n
        n += 1
        print("  [%s] %s" % ("OK " if cond else "BAD", name))
        if not cond:
            bad.append(name)

    def par(rows, ledger_lines):
        lp = _mkledger(tmpdir, ledger_lines) if ledger_lines is not None else \
            os.path.join(tempfile.mkdtemp(dir=tmpdir), "absent.txt")
        try:
            return True, p._w_from_record(rows, lp, infra=[])
        except p.Refusal as e:
            return False, str(e)

    def gsc(rows, ledger_lines):
        lp = _mkledger(tmpdir, ledger_lines) if ledger_lines is not None else \
            os.path.join(tempfile.mkdtemp(dir=tmpdir), "absent.txt")
        try:
            return True, _w_from_record_gscan(rows, lp, infra=[])
        except Refusal as e:
            return False, str(e)

    print("-" * 78)
    print("DIRECTION 1 -- ON THE PARENT'S OWN DOMAIN (window-homogeneous row sets),")
    print("               --gscan REFUSES EVERYTHING, the parent's ACCEPTS included.")
    print("-" * 78)
    WP = p.W_PRIMARY
    homog = [
        ("5 clean rows at W_PRIMARY + agreeing ledger",
         [{"name": "S%d" % i, "W": WP} for i in range(5)], ["W_STEPS=%d" % WP]),
        ("5 clean rows at W_PRIMARY + ABSENT ledger",
         [{"name": "S%d" % i, "W": WP} for i in range(5)], None),
        ("1 clean row at W_PRIMARY + agreeing ledger",
         [{"name": "S5", "W": WP}], ["W_STEPS=%d" % WP]),
        ("33 clean rows at W_PRIMARY + agreeing ledger",
         [{"name": "S%d" % i, "W": WP} for i in range(33)], ["W_STEPS=%d" % WP]),
        # THE SHARPEST CASE IN DIRECTION 1, and the one the M-D mutant breaks: a
        # window-homogeneous set that is FULLY LEG-LABELLED and internally perfect. Every
        # limb gscan shares with the parent PASSES on it; only the leg-set closure (N4)
        # refuses it, because two of the three registered legs are absent. Without this
        # row the other homogeneous inputs refuse on the missing `leg` key instead, and
        # deleting the closure would go unnoticed.
        ("5 rows at W_PRIMARY, ALL LABELLED leg A0, ledger carries W_STEPS_A0 too",
         [{"name": "S5" if i == 0 else "S%d" % i, "W": WP, "leg": "A0"} for i in range(5)],
         ["W_STEPS=%d" % WP, "W_STEPS_A0=%d" % WP]),
        ("rows at W_PRIMARY, one missing its W key",
         [{"name": "S%d" % i, "W": WP} for i in range(4)] + [{"name": "S4"}],
         ["W_STEPS=%d" % WP]),
        ("rows disagreeing (one at 300)",
         [{"name": "S%d" % i, "W": WP} for i in range(4)] + [{"name": "S4", "W": 300}],
         ["W_STEPS=%d" % WP]),
        ("rows and ledger agree on 300, not W_PRIMARY",
         [{"name": "S%d" % i, "W": 300} for i in range(5)], ["W_STEPS=300"]),
        ("ledger carries two W_STEPS lines",
         [{"name": "S%d" % i, "W": WP} for i in range(5)],
         ["W_STEPS=%d" % WP, "W_STEPS=%d" % WP]),
        ("ledger W_STEPS=900 against rows at W_PRIMARY",
         [{"name": "S%d" % i, "W": WP} for i in range(5)], ["W_STEPS=900"]),
        ("a row carrying an unparseable W",
         [{"name": "S%d" % i, "W": WP} for i in range(4)] + [{"name": "S4", "W": "two"}],
         ["W_STEPS=%d" % WP]),
    ]
    par_accepts = 0
    gsc_accepts = 0
    for label, rows, led in homog:
        pa, pv = par(rows, led)
        ga, gv = gsc(rows, led)
        par_accepts += 1 if pa else 0
        gsc_accepts += 1 if ga else 0
        unit("D1 %-52s parent=%-6s gscan=%s" % (label[:52], "ACCEPT" if pa else "refuse",
                                                "ACCEPT" if ga else "REFUSE"),
             not ga)
    unit("D1-VACUITY the parent ACCEPTED %d of %d homogeneous inputs -- the direction is "
         "not a battery of inputs the parent also rejected" % (par_accepts, len(homog)),
         par_accepts >= 3)
    unit("D1-TOTAL --gscan accepted %d of %d inputs on the parent's own domain (must be 0)"
         % (gsc_accepts, len(homog)), gsc_accepts == 0)

    print("-" * 78)
    print("DIRECTION 2 -- OFF THAT DOMAIN, THE PARENT'S FIVE STRUCTURAL LIMBS STILL RUN,")
    print("               PER LEG.  Each mutation is applied to leg A1 of a three-leg set")
    print("               and to the parent's own single-window equivalent.")
    print("-" * 78)
    clean_rows = _clean_gscan_rows()
    clean_led = _clean_gscan_ledger_lines()
    ok, v = gsc(clean_rows, clean_led)
    unit("D2-POS the CLEAN three-leg set is ACCEPTED and returns the registered leg map %r"
         % (dict(LEG_W),), ok and v == dict(LEG_W))
    okp, vp = par([{"name": "S%d" % i, "W": WP} for i in range(5)], ["W_STEPS=%d" % WP])
    unit("D2-POS-PARENT the parent's own clean single-window set is ACCEPTED (returns %r) "
         "-- without this the battery below proves only that both refuse everything" % (vp,),
         okp and vp == WP)

    def mut_rows(fn):
        rs = [dict(r) for r in _clean_gscan_rows()]
        return fn(rs)

    def parent_equiv(fn):
        """the SAME structural defect on a single-window set the parent governs"""
        rs = [{"name": "S%d" % i, "W": WP} for i in range(4)]
        return fn(rs)

    shared = [
        ("L1 a row carries no W key",
         lambda rs: [({k: v for k, v in r.items() if k != "W"} if r["leg"] == "A1" and
                      r["name"] == "S2a" else r) for r in rs],
         lambda rs: rs[:3] + [{"name": "S3"}]),
        ("L2 a row carries an unparseable W",
         lambda rs: [(dict(r, W="fourteen hundred") if r["leg"] == "A1" and
                      r["name"] == "S2a" else r) for r in rs],
         lambda rs: rs[:3] + [{"name": "S3", "W": "two thousand"}]),
        ("L3 rows inside one leg disagree on W",
         lambda rs: [(dict(r, W=1399) if r["leg"] == "A1" and r["name"] == "S2a" else r)
                     for r in rs],
         lambda rs: rs[:3] + [{"name": "S3", "W": 300}]),
    ]
    for label, gmut, pmut in shared:
        ga, gv = gsc(mut_rows(gmut), clean_led)
        pa, pv = par(parent_equiv(pmut), ["W_STEPS=%d" % WP])
        unit("D2 %-44s parent=%-6s gscan=%s  (both must REFUSE)"
             % (label, "ACCEPT" if pa else "REFUSE", "ACCEPT" if ga else "REFUSE"),
             (not ga) and (not pa))
    # L4 / L5 are per-leg ledger limbs; the parent's equivalents are on its single line.
    ga, _ = gsc(clean_rows, ["W_STEPS_A0=2000", "W_STEPS_A1=1400", "W_STEPS_A1=1400",
                             "W_STEPS_A2=3000"])
    pa, _ = par([{"name": "S%d" % i, "W": WP} for i in range(4)],
                ["W_STEPS=%d" % WP, "W_STEPS=%d" % WP])
    unit("D2 L4 a leg's ledger line is DOUBLED                    parent=%-6s gscan=%s  "
         "(both must REFUSE)" % ("ACCEPT" if pa else "REFUSE", "ACCEPT" if ga else "REFUSE"),
         (not ga) and (not pa))
    ga, _ = gsc(clean_rows, ["W_STEPS_A0=2000", "W_STEPS_A1=999", "W_STEPS_A2=3000"])
    pa, _ = par([{"name": "S%d" % i, "W": WP} for i in range(4)], ["W_STEPS=999"])
    unit("D2 L5 a leg's ledger line DISAGREES with its rows       parent=%-6s gscan=%s  "
         "(both must REFUSE)" % ("ACCEPT" if pa else "REFUSE", "ACCEPT" if ga else "REFUSE"),
         (not ga) and (not pa))

    print("-" * 78)
    print("DIRECTION 3 -- THE SEVEN REFUSALS THE PARENT CANNOT EXPRESS.  Each is paired")
    print("               with the parent ACCEPTING the same defect once relabelled, which")
    print("               is what makes it an ADDED constraint and not a re-labelled one.")
    print("-" * 78)
    only = [
        ("N1 a row carries no `leg` key",
         lambda rs: [({k: v for k, v in r.items() if k != "leg"} if r["name"] == "S2a" and
                      r["W"] == 1400 else r) for r in rs],
         [{"name": "S%d" % i, "W": WP} for i in range(4)]),
        ("N2 a row carries an unregistered leg `A9`",
         lambda rs: [(dict(r, leg="A9") if r["leg"] == "A1" and r["name"] == "S2a" else r)
                     for r in rs],
         [dict({"name": "S%d" % i, "W": WP}, leg="A9") for i in range(4)]),
        ("N3 leg A1's rows are filed under leg A0 (the MISLABEL)",
         lambda rs: [(dict(r, leg="A0") if r["leg"] == "A1" else r) for r in rs],
         [dict({"name": "S%d" % i, "W": WP}, leg="A0") for i in range(4)]),
        ("N4 leg A2 is MISSING entirely",
         lambda rs: [r for r in rs if r["leg"] != "A2"],
         [dict({"name": "S%d" % i, "W": WP}, leg="A0") for i in range(4)]),
        ("N4 an EXTRA leg `A3` at an unregistered W=2400",
         lambda rs: rs + [{"name": "S5", "leg": "A3", "W": 2400, "dobj_dshape": [1.0]}],
         [dict({"name": "S%d" % i, "W": WP}, leg="A0") for i in range(4)]),
        ("N6 leg A0 carries a SECOND S5 row (a re-fired stage)",
         lambda rs: rs + [{"name": "S5", "leg": "A0", "W": 2000, "dobj_dshape": [9.0]}],
         [dict({"name": "S5", "W": WP}, leg="A0") for _ in range(2)]),
    ]
    for label, gmut, prows in only:
        ga, gv = gsc(mut_rows(gmut), clean_led)
        pa, pv = par(prows, ["W_STEPS=%d" % WP])
        unit("D3 %-52s gscan=%-6s parent(relabelled)=%s"
             % (label[:52], "REFUSE" if not ga else "ACCEPT",
                "ACCEPT" if pa else "refuse"),
             (not ga) and pa)
    swapped = [dict(r) for r in _clean_gscan_rows()]
    for r in swapped:
        if r["leg"] == "A1":
            r["W"] = 3000
        elif r["leg"] == "A2":
            r["W"] = 1400
    ga, gv = gsc(swapped, ["W_STEPS_A0=2000", "W_STEPS_A1=3000", "W_STEPS_A2=1400"])
    pa, _ = par([{"name": "S%d" % i, "W": WP} for i in range(4)], ["W_STEPS=%d" % WP])
    unit("D3 N3 legs A1 and A2 have their windows SWAPPED -- every leg present, every leg "
         "internally homogeneous, the ledger agreeing with the rows, and the whole thing "
         "still grading the WRONG WINDOW under the RIGHT LEG NAME (W2R-GRADER-DEF-1's "
         "exact shape). gscan=%s parent(relabelled)=%s"
         % ("REFUSE" if not ga else "ACCEPT", "ACCEPT" if pa else "refuse"),
         (not ga) and pa and "N3" in gv)
    ga, _ = gsc(clean_rows, ["W_STEPS_A0=2000", "W_STEPS_A2=3000"])
    pa, _ = par([{"name": "S%d" % i, "W": WP} for i in range(4)], ["W_STEPS=%d" % WP])
    unit("D3 N7 a leg's ledger line is ABSENT while the others are present  gscan=%s "
         "parent(relabelled)=%s" % ("REFUSE" if not ga else "ACCEPT",
                                    "ACCEPT" if pa else "refuse"),
         (not ga) and pa)

    print("-" * 78)
    print("DIRECTION 4 -- THE ABSENT-LEDGER BRANCH, which is the parent's OWN L-342")
    print("               reasoning and must not become a way to lose the windows.")
    print("-" * 78)
    inf = []
    lp = os.path.join(tempfile.mkdtemp(dir=tmpdir), "absent.txt")
    okA = True
    try:
        vA = _w_from_record_gscan(clean_rows, lp, infra=inf)
    except Refusal:
        okA = False
        vA = None
    unit("D4 ledger ABSENT + a clean three-leg set -> accepted, CROSS-READ reported as "
         "INFRASTRUCTURE (1 note), legs still %r" % (dict(LEG_W),),
         okA and vA == dict(LEG_W) and len(inf) == 1 and "NOT MEASURED" in inf[0])
    ga, gv = gsc(mut_rows(lambda rs: [(dict(r, W=1399) if r["leg"] == "A1" else r)
                                      for r in rs]), None)
    unit("D4 ledger ABSENT + leg A1 at W=1399 -> STILL REFUSED. The absent ledger buys "
         "nothing: the window is PHYSICS and is checked against a typed constant",
         (not ga) and "N3" in gv)

    check(n > 0, "NARROWING SELFTEST RAN ZERO UNITS: a battery that ran nothing has not passed")
    print("NARROWING SELFTEST units=%d failures=%d python_O=%s" % (n, len(bad), not __debug__))
    if bad:
        print("NARROWING SELFTEST FAIL: %s" % bad)
        return 2
    print("NARROWING SELFTEST PASS %d/%d" % (n, n))
    return 0


def selftest(tmpdir):
    """The instrument battery: the bar, the plants, the ceiling guard, the arithmetic."""
    n = 0
    bad = []

    def unit(name, cond):
        nonlocal n
        n += 1
        print("  [%s] %s" % ("OK " if cond else "BAD", name))
        if not cond:
            bad.append(name)

    def refuses(fn, *a, **k):
        try:
            fn(*a, **k)
            return False
        except Refusal:
            return True

    # ---- 1. the parent pin, and the AST audit of THIS file
    p = parent()
    unit("U01 the frozen parent imports and its md5 is the pinned %s" % PARENT_MD5,
         p is not None and _md5(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             PARENT_NAME)) == PARENT_MD5)
    na = _count_assert_statements(os.path.abspath(__file__))
    unit("U02 this file carries %d `assert` STATEMENTS by AST (must be 0; `python3 -O` "
         "deletes them and a guard that vanishes under a flag is not a guard)" % na, na == 0)
    unit("U03 the inherited constants agree with the parent: C_ENV=%r h_max=%r eps=%r"
         % (p.C_ENV, p.H_MAX, p.EPS_NOISE_TARGET),
         p.C_ENV == C_ENV_EXPECTED and p.H_MAX == H_MAX_EXPECTED
         and p.EPS_NOISE_TARGET == EPS_NOISE_TARGET_EXPECTED)

    # ---- 2. the arithmetic, DERIVED not typed
    req = wg_required()
    unit("U04 the admissibility requirement W*|g| >= %.4f is DERIVED from C_ENV/eps/h_max, "
         "not typed" % req, abs(req - 1781.4) < 1e-6)
    unit("U05 the FS-1 bar is %.4f = requirement x margin %.2f" % (fs1_bar(), FS1_MARGIN),
         abs(fs1_bar() - req * FS1_MARGIN) < 1e-12 and abs(fs1_bar() - 2048.61) < 1e-6)
    unit("U06 h_min at the W3 anchor recomputes the artefact's 0.0911930188193242 from "
         "100*C_ENV/(W*|g|)",
         abs((100.0 * p.C_ENV) / (W_ANCHOR * abs(G_ANCHOR)) - 0.0911930188193242) < 1e-9)

    # ---- 3. BAR-1 / BAR-2 / BAR-3
    unit("U07 BAR-1 the gscan sizing entry point RAISES, always", refuses(_step_plan_refusal))
    unit("U08 BAR-1 it raises even when handed the arguments a real sizing call would take",
         refuses(_step_plan_refusal, 4.4535e-4, 0.48835975139977306))
    unit("U09 BAR-3 accepts an artefact carrying the registered refusal string",
         _bar_admissible({"admissible": BAR_REFUSAL_STRING,
                          "step_plan": BAR_REFUSAL_STRING})["verdict"] == "PASS")
    for k, v in (("admissible", True), ("admissible", False), ("steps", [0.01, 0.02]),
                 ("h_min", 0.039), ("h_star", 0.01), ("step_plan", {"steps": [1]})):
        unit("U10 BAR-3 REFUSES a planted %s=%r at the top level" % (k, v),
             refuses(_bar_admissible, {k: v}))
    unit("U11 BAR-3 REFUSES a planted admissible=true NESTED three deep -- the bar walks "
         "the object, it does not check the top level",
         refuses(_bar_admissible, {"gates": [{"a": {"b": {"admissible": True}}}]}))
    unit("U12 BAR-3 REFUSES a planted step list inside a LIST element",
         refuses(_bar_admissible, {"gates": [{"steps": [0.01]}]}))
    unit("U13 BAR-2's detector sees a three-leg manifest as gscan data",
         looks_like_gscan(_clean_gscan_rows()) is True)
    unit("U14 BAR-2's detector does NOT mistake a homogeneous W3 manifest for gscan data",
         looks_like_gscan([{"name": "S%d" % i, "W": 2000} for i in range(5)]) is False)
    unit("U15 BAR-2's detector catches a manifest carrying `leg` keys even at one window",
         looks_like_gscan([{"name": "S5", "W": 2000, "leg": "A0"}]) is True)

    # ---- 4. rule-3 plants, each shown able to FAIL
    r = ga_p1_plant_g()
    unit("U16 GA-P1 the |g| reader SEES the planted %g and refuses both zero shapes %r"
         % (PLANT_G, r["refused_directions"]),
         r["verdict"] == "PASS" and abs(r["read_back"] - PLANT_G) < 1e-15
         and len(r["refused_directions"]) == 2)
    unit("U17 GA-1 REFUSES an exactly-zero gradient component by name",
         refuses(read_g, [{"name": "S5", "leg": "A0", "W": 2000,
                           "dobj_dshape": [0.0, 1.0]}], "A0"))
    unit("U18 GA-1 REFUSES a non-finite gradient component",
         refuses(read_g, [{"name": "S5", "leg": "A0", "W": 2000,
                           "dobj_dshape": [float('nan')]}], "A0"))
    unit("U19 GA-1 REFUSES when the registered sizing component is past the end of the "
         "gradient vector",
         refuses(read_g, [{"name": "S5", "leg": "A0", "W": 2000, "dobj_dshape": []}], "A0"))
    r2 = ga_p2_plant_binding(tmpdir)
    unit("U20 GA-P2 the binding accepted its clean control AND refused a planted mislabel",
         r2["verdict"] == "PASS")
    r3 = ga_p3_plant_spend(tmpdir)
    unit("U21 GA-P3 the spend reader SAW the planted %s core-min and returned UNMEASURED in "
         "all three named directions" % PLANT_SPEND_CORE_MIN,
         r3["verdict"] == "PASS" and abs(r3["read_back"] - PLANT_SPEND_CORE_MIN) < 1e-9
         and len(r3["refused_directions"]) == 3)

    # ---- 5. the ceiling guard, DRIVEN in every branch
    base = tempfile.mkdtemp(dir=tmpdir, prefix="ceil_")
    fresh = os.path.join(base, "fresh")
    rc, body = cumulative_item_ceiling_census("A0", [fresh], tmpdir)
    unit("U22 CEILING a FRESH root (neither root nor ledger) -> rc=0, spent 0.000",
         rc == 0 and abs(body["spent_core_min"]) < 1e-12)
    r_spent = os.path.join(base, "spent")
    os.makedirs(r_spent)
    with open(os.path.join(r_spent, "ledger.txt"), "w") as f:
        f.write("STAGE=S0 TASK=mesh rc=0 core_min=1.750\n"
                "STAGE=S5 TASK=compute_totals rc=0 core_min=66.780\n")
    rc, body = cumulative_item_ceiling_census("A1", [r_spent], tmpdir)
    unit("U23 CEILING 68.530 spent + leg A1 cap 70.0 = %.3f <= ceiling 330.0 -> rc=0"
         % body["projected_worst_case"],
         rc == 0 and abs(body["spent_core_min"] - 68.53) < 1e-9)
    r_big = os.path.join(base, "big")
    os.makedirs(r_big)
    with open(os.path.join(r_big, "ledger.txt"), "w") as f:
        f.write("STAGE=S5 rc=0 core_min=200.0\n")
    rc, body = cumulative_item_ceiling_census("A2", [r_big], tmpdir)
    unit("U24 CEILING 200.0 spent + leg A2 cap 155.0 = 355.0 > 330.0 -> rc=6 and the run "
         "STOPS; it does not get a new budget", rc == 6 and "ITEM CEILING" in body["reason"])
    r_um = os.path.join(base, "unmeasured")
    os.makedirs(r_um)
    with open(os.path.join(r_um, "ledger.txt"), "w") as f:
        f.write("STAGE=S5 TASK=compute_totals rc=0 wall_s=4073\n")
    rc, body = cumulative_item_ceiling_census("A0", [r_um], tmpdir)
    unit("U25 CEILING a spend-shaped ledger line with NO core_min= -> rc=65 UNMEASURED, "
         "NOT a zero (this is the limb d6rf lacks: its awk would have summed 0)",
         rc == 65 and "UNMEASURED" in body["reason"])
    r_nl = os.path.join(base, "noledger")
    os.makedirs(r_nl)
    open(os.path.join(r_nl, "S5_x.log"), "w").write("x\n")
    rc, body = cumulative_item_ceiling_census("A0", [r_nl], tmpdir)
    unit("U26 CEILING a root that EXISTS with stage logs and NO ledger -> rc=65 UNMEASURED "
         "(the limb a1wrt lacks: it reads a missing ledger as 0.0 unconditionally)",
         rc == 65 and "UNMEASURED" in body["reason"])
    r_bad = os.path.join(base, "malformed")
    os.makedirs(r_bad)
    with open(os.path.join(r_bad, "ledger.txt"), "w") as f:
        f.write("STAGE=S5 TASK=compute_totals rc=0 core_min=1.2.3 memavail_GiB=20.0\n")
    rc, body = cumulative_item_ceiling_census("A0", [r_bad], tmpdir)
    unit("U25b CEILING a MALFORMED core_min=1.2.3 -> rc=65 UNMEASURED. d6rf's `[0-9.]+` "
         "matches `1.2` out of it and returns a WRONG NUMBER, and its float() ValueError "
         "is not caught at all -- $SPENT comes back EMPTY and its guard FAILS OPEN. The "
         "token is captured WHOLE here and validated WHOLE.",
         rc == 65 and "UNMEASURED" in body["reason"])
    for tok in ("core_min=", "core_min=-4.0", "core_min=nan", "core_min=1e"):
        r_t = tempfile.mkdtemp(dir=base)
        with open(os.path.join(r_t, "ledger.txt"), "w") as f:
            f.write("STAGE=S5 rc=0 %s memavail_GiB=20.0\n" % tok)
        rc, body = cumulative_item_ceiling_census("A0", [r_t], tmpdir)
        unit("U25c CEILING a spend row carrying `%s` -> rc=65 UNMEASURED, never a number"
             % tok, rc == 65)
    r_sci = tempfile.mkdtemp(dir=base)
    with open(os.path.join(r_sci, "ledger.txt"), "w") as f:
        f.write("STAGE=S5 rc=0 core_min=6.6780e+01 memavail_GiB=20.0\n")
    rc, body = cumulative_item_ceiling_census("A0", [r_sci], tmpdir)
    unit("U25d CEILING a LEGITIMATE scientific-notation core_min=6.6780e+01 is READ, not "
         "refused -- a validator that refuses everything is not a validator",
         rc == 0 and abs(body["spent_core_min"] - 66.78) < 1e-9)
    r_ab = os.path.join(base, "already")
    os.makedirs(r_ab)
    with open(os.path.join(r_ab, "ledger.txt"), "w") as f:
        f.write("STAGE=S5 rc=0 core_min=10.0\nLEG=A0 stage=S5 rc=0 core_min=66.78\n")
    rc, body = cumulative_item_ceiling_census("A0", [r_ab], tmpdir)
    unit("U27 CEILING leg A0 already carries an rc=0 ledger row -> rc=6 ALREADY_BOUGHT; a "
         "second record for one run is the defect (d6rf:149-153)",
         rc == 6 and "ALREADY_BOUGHT" in body["reason"])
    unit("U26b CEILING the ledger-absent case is SPLIT, not blanket: absent root AND "
         "absent ledger is FRESH (0.000, U22); present root with logs and absent ledger "
         "is UNMEASURED (rc=65, U26). A blanket refusal on an absent ledger would make a "
         "first leg unlaunchable forever; a blanket 0.0 is the planted zero.",
         cumulative_item_ceiling_census("A0", [fresh], tmpdir)[0] == 0
         and cumulative_item_ceiling_census("A0", [r_nl], tmpdir)[0] == 65)
    rc, body = cumulative_item_ceiling_census("A9", [fresh], tmpdir)
    unit("U28 CEILING an unregistered leg -> rc=64; there is no cap to compare against",
         rc == 64)
    rc, body = cumulative_item_ceiling_census("A0", [r_spent, r_big], tmpdir)
    unit("U29 CEILING spend is CUMULATIVE ACROSS ROOTS: 68.53 + 200.0 + leg cap 100.0 = "
         "368.53 > 330.0 -> rc=6. A per-arm cap alone cannot see an item walking past its "
         "ceiling one arm at a time.", rc == 6)
    unit("U30 CEILING the registered leg caps sum to %.1f, EXACTLY the item ceiling %.1f "
         "-- checked, not assumed" % (sum(LEG_CAP_CORE_MIN.values()), ITEM_CEILING_CORE_MIN),
         abs(sum(LEG_CAP_CORE_MIN.values()) - ITEM_CEILING_CORE_MIN) < 1e-9)

    # ---- 6. FS-0 and FS-1 arithmetic
    per = {"A0": {"W": 2000, "abs_g": abs(G_ANCHOR),
                  "W_times_abs_g": 2000 * abs(G_ANCHOR)},
           "A1": {"W": 1400, "abs_g": 0.713, "W_times_abs_g": 1400 * 0.713},
           "A2": {"W": 3000, "abs_g": 0.318, "W_times_abs_g": 3000 * 0.318}}
    unit("U31 FS-0 an exact reproduction of the anchor -> HIT",
         ga_2_fs0(per)["outcome"] == "HIT")
    per_off = dict(per)
    per_off["A0"] = dict(per["A0"], abs_g=abs(G_ANCHOR) * 1.005)
    unit("U32 FS-0 +0.5 %% (inside the registered +/-1 %% band) -> HIT",
         ga_2_fs0(per_off)["outcome"] == "HIT")
    per_off2 = dict(per)
    per_off2["A0"] = dict(per["A0"], abs_g=abs(G_ANCHOR) * 1.02)
    r = ga_2_fs0(per_off2)
    unit("U33 FS-0 +2 %% -> MISS, verdict NOT A RESULT, and the arm stops at leg A0",
         r["outcome"] == "MISS" and r["verdict"] == "NOT A RESULT")
    priors = [(w, g, "typed") for w, g, _ in PRIOR_LEGS]
    r = ga_3_fs1(per, priors)
    unit("U34 FS-1 on the registration's own PREDICTED point set -> MISS (max W*|g| = "
         "%.2f against the bar %.2f); Arm B launches nothing"
         % (r["max_W_times_abs_g"], r["bar"]),
         r["outcome"] == "MISS" and r["arm_b_fires"] is False and r["W_adm"] is None)
    per_hit = dict(per)
    per_hit["A2"] = {"W": 3000, "abs_g": 0.70, "W_times_abs_g": 2100.0}
    r = ga_3_fs1(per_hit, priors)
    unit("U35 FS-1 the FALSIFIER: a planted |g(3000)|=0.70 gives W*|g|=2100 > %.2f -> HIT "
         "at W_adm=3000, Arm B fires. The gate can go both ways." % fs1_bar(),
         r["outcome"] == "HIT" and r["W_adm"] == 3000 and r["arm_b_fires"] is True)
    per_two = dict(per_hit)
    per_two["A1"] = {"W": 1400, "abs_g": 1.6, "W_times_abs_g": 2240.0}
    r = ga_3_fs1(per_two, priors)
    unit("U36 FS-1 W_adm is the SMALLEST clearing window (1400, not 3000) -- the rule is "
         "registered, not chosen after the data", r["W_adm"] == 1400)
    unit("U37 FS-1's MISS note SCOPES itself to the measured set and claims no enumeration "
         "beyond it", "says nothing about W >" in ga_3_fs1(per, priors)["note"])

    # ---- 7. the verdict vocabulary
    unit("U38 every verdict this file can emit is in the fixed vocabulary",
         set(["PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"])
         >= {ga_2_fs0(per)["verdict"], ga_2_fs0(per_off2)["verdict"],
             ga_3_fs1(per, priors)["verdict"],
             cumulative_item_ceiling_census("A2", [r_big], tmpdir)[1]["verdict"]})

    check(n > 0, "W3S SELFTEST RAN ZERO UNITS: a battery that ran nothing has not passed")
    print("W3S SELFTEST units=%d failures=%d python_O=%s" % (n, len(bad), not __debug__))
    if bad:
        print("W3S SELFTEST FAIL: %s" % bad)
        return 2
    print("W3S SELFTEST PASS %d/%d" % (n, n))
    return 0


def _count_assert_statements(path):
    """Count `assert` STATEMENTS by AST -- statement type, not behaviour.  A grep would
    match `raise AssertionError`, a docstring or a variable called `assert_state`; a
    behavioural test would pass a file whose asserts all happen to hold.  Only the
    statement type distinguishes `assert X`, which `-O` DELETES, from `if not X: raise`,
    which it does not."""
    import ast as _ast
    try:
        with open(path) as f:
            t = _ast.parse(f.read())
    except Exception:                                          # noqa: BLE001
        return -1
    return sum(1 for nd in _ast.walk(t) if isinstance(nd, _ast.Assert))


def _count_asserts_outside_selftest(path):
    """The stricter reading the brief asks for: `assert` statements OUTSIDE the selftest
    functions.  Reported beside the whole-file count so a reader can see both."""
    import ast as _ast
    try:
        with open(path) as f:
            t = _ast.parse(f.read())
    except Exception:                                          # noqa: BLE001
        return -1
    st = {"selftest", "selftest_narrowing", "olimb"}
    inside = 0
    for nd in _ast.walk(t):
        if isinstance(nd, _ast.FunctionDef) and nd.name in st:
            inside += sum(1 for x in _ast.walk(nd) if isinstance(x, _ast.Assert))
    return _count_assert_statements(path) - inside


def olimb(tmpdir):
    """`--olimb` : MUTATE THIS FILE, then require BOTH `python3` and `python3 -O` to catch
    every mutant.  Running the battery on healthy input under both flags proves nothing --
    healthy input passes either way, so identical output is exactly what a COMPLETELY
    DISABLED battery produces."""
    import re as _re
    import shutil as _sh
    import subprocess as _sp
    here = os.path.abspath(__file__)
    os.makedirs(tmpdir, exist_ok=True)
    src = open(here).read()
    results = []
    # A mutant loads the FROZEN parent from beside ITSELF, so the parent is copied into
    # the mutant directory and its md5 re-checked there.  Copying it is not editing it:
    # the copy is verified byte-identical before any mutant runs, and a mutant that could
    # not find the parent would fail for the wrong reason and read as a caught mutant.
    _sh.copyfile(os.path.join(os.path.dirname(here), PARENT_NAME),
                 os.path.join(tmpdir, PARENT_NAME))
    if _md5(os.path.join(tmpdir, PARENT_NAME)) != PARENT_MD5:
        raise Refusal("--olimb: the parent copy in %s is not byte-identical to the frozen "
                      "parent; every mutant would then fail for the wrong reason" % tmpdir)

    def run(path, flag, arg):
        cmd = [sys.executable] + (["-O"] if flag else []) + [path, arg,
                                                             "--tmpdir", tmpdir]
        pr = _sp.run(cmd, capture_output=True, text=True)
        return pr.returncode

    for flag in (False, True):
        for arg in ("--selftest", "--selftest-narrowing"):
            rc = run(here, flag, arg)
            results.append(("control unmutated %s" % arg, "-O" if flag else "  ",
                            rc, rc == 0))

    mutants = [
        ("M-A gate mutant: FS1_MARGIN 1.15 -> 0.10",
         r"^FS1_MARGIN = 1\.15", "FS1_MARGIN = 0.10", "--selftest"),
        ("M-B statement type: one check() -> assert",
         r"^(\s*)check\((.+), (.+)\)$", r"\g<1>assert \g<2>, \g<3>", "--selftest"),
        ("M-C falsifier mutant: FS0_TOL_REL 0.01 -> 10.0",
         r"^FS0_TOL_REL = 0\.01", "FS0_TOL_REL = 10.0", "--selftest"),
        # M-D TARGETS N3, NOT THE LEG-SET CLOSURE, AND THE REASON IS A MEASUREMENT.
        # The closure is OVER-DETERMINED by three limbs -- N2 gives leg set (subset of)
        # LEG_NAMES, N4 gives equality, and the per-leg ZERO-ROWS refusal gives
        # (superset of) -- so deleting any ONE of the three is MASKED by the other two and
        # the mutant survives for the wrong reason. That over-determination is a GOOD
        # property of the binding and it is why no useful mutant exists there. N3 (each
        # leg's W equals ITS OWN registered window) is the one limb in the binding that
        # nothing else covers: delete it and a leg-window SWAP grades the wrong window
        # under the right leg name, which is W2R-GRADER-DEF-1 exactly.
        ("M-D THE NARROWING mutant: N3, the per-leg registered-window pin, deleted",
         r"^        if w != LEG_W\[leg\]:", "        if False:",
         "--selftest-narrowing"),
        ("M-E ceiling mutant: an UNMEASURED prior spend read as 0.0",
         r'^        return None, \("UNMEASURED: %d spend-shaped',
         '        return 0.0, ("UNMEASURED: %d spend-shaped', "--selftest"),
    ]
    for name, pat, rep, arg in mutants:
        mp = os.path.join(tmpdir, "mutant_%s.py" % name.split()[0].replace("-", ""))
        s2, k = _re.subn(pat, rep, src, count=1, flags=_re.M)
        if k != 1:
            raise Refusal("--olimb could not build mutant %r; its target line moved" % name)
        with open(mp, "w") as f:
            f.write(s2)
        # the mutant must load the frozen parent from the real case directory
        for flag in (False, True):
            rc = run(mp, flag, arg)
            results.append((name, "-O" if flag else "  ", rc, rc != 0))

    print("=" * 78)
    print("`python3 -O` LIMB -- a battery is flag-proof only if it still CATCHES under -O")
    print("=" * 78)
    ok = True
    for name, flag, rc, good in results:
        ok = ok and good
        print("  %-58s %s rc=%d  %s" % (name[:58], flag, rc, "OK" if good else "*** BAD ***"))
    print("")
    print("  M-D is the one this instrument exists for: deleting the leg-set closure turns")
    print("  the --gscan binding from a NARROWING into a RELAXATION, and the narrowing")
    print("  selftest is what notices.")
    print("")
    print("  %s" % ("-O LIMB PASSES" if ok else "*** -O LIMB FAILS ***"))
    _sh.rmtree(os.path.join(tmpdir, "mutant_scratch"), ignore_errors=True)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-narrowing", dest="selftest_narrowing", action="store_true")
    ap.add_argument("--olimb", action="store_true")
    ap.add_argument("--assert-audit", dest="assert_audit", action="store_true")
    ap.add_argument("--gatelist", action="store_true")
    ap.add_argument("--parent-check", dest="parent_check", action="store_true")
    ap.add_argument("--gscan", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--plan2", action="store_true")
    ap.add_argument("--plan3", action="store_true")
    ap.add_argument("--cumulative-item-ceiling", dest="ceiling_census",
                    action="store_true")
    ap.add_argument("--leg", default=None)
    ap.add_argument("--root", default=None, action="append")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if a.gatelist:
        print("\n".join(GATES_EMITTED))
        return 0
    if a.assert_audit:
        here = os.path.abspath(__file__)
        n = _count_assert_statements(here)
        out = _count_asserts_outside_selftest(here)
        print("assert statements in this file: %d (must be 0)" % n)
        print("assert statements OUTSIDE the selftest functions: %d (must be 0)" % out)
        return 0 if (n == 0 and out == 0) else 1
    if a.parent_check:
        try:
            parent()
        except Refusal as e:
            print("REFUSAL: %s" % e, file=sys.stderr)
            return 2
        print("PARENT OK %s md5=%s UNEDITED" % (PARENT_NAME, PARENT_MD5))
        return 0
    if a.olimb:
        return olimb(os.path.join(a.tmpdir, "w3s_olimb"))
    if a.selftest_narrowing:
        d = os.path.join(a.tmpdir, "w3s_narrowing")
        os.makedirs(d, exist_ok=True)
        try:
            return selftest_narrowing(d)
        except (Refusal, SelfTestFailure) as e:
            print("SELFTEST ABORTED: %s" % e, file=sys.stderr)
            return 2
    if a.selftest:
        d = os.path.join(a.tmpdir, "w3s_selftest")
        os.makedirs(d, exist_ok=True)
        try:
            return selftest(d)
        except (Refusal, SelfTestFailure) as e:
            print("SELFTEST ABORTED: %s" % e, file=sys.stderr)
            return 2
    if a.ceiling_census:
        if not (a.leg and a.root):
            print("REFUSAL: --cumulative-item-ceiling needs --leg and at least one --root",
                  file=sys.stderr)
            return 3
        try:
            rc, body = cumulative_item_ceiling_census(a.leg, a.root, a.tmpdir)
        except Refusal as e:
            print("REFUSAL: %s" % e, file=sys.stderr)
            return 65
        print(json.dumps(body, indent=2, sort_keys=True, default=str))
        return rc
    # ---- BAR-2: a step-plan request on gscan data REFUSES, before any gate runs.
    if a.plan or a.plan2 or a.plan3:
        if a.manifest and os.path.isfile(a.manifest):
            try:
                rows = _read_manifest_rows(a.manifest)
            except Exception as e:                             # noqa: BLE001
                print("REFUSAL: %s" % e, file=sys.stderr)
                return 2
            if looks_like_gscan(rows):
                print("REFUSAL: GA-BAR / BAR-2: --plan was requested on a GSCAN manifest "
                      "(%d distinct windows / `leg` keys present). %s"
                      % (len({r.get("W") for r in rows}), BAR_REFUSAL_STRING),
                      file=sys.stderr)
                return 2
        print("REFUSAL: this successor grades `--gscan` only. The step-plan phases belong "
              "to Arm B and to the FROZEN parent %s, which is not edited (CLAUDE.md rule 6)."
              % PARENT_NAME, file=sys.stderr)
        return 2
    if a.gscan:
        if not (a.manifest and a.root and len(a.root) == 1):
            print("REFUSAL: --gscan needs --manifest and exactly one --root",
                  file=sys.stderr)
            return 3
        try:
            res = plan_gscan(a.manifest, a.root[0], a.tmpdir)
        except Refusal as e:
            print("REFUSAL: %s" % e, file=sys.stderr)
            return 2
        txt = json.dumps(res, indent=2, sort_keys=True, default=str)
        print(txt)
        if a.out:
            with open(a.out, "w") as f:
                f.write(txt)
        return 0
    print("REFUSAL: no mode selected. Try --selftest, --selftest-narrowing, --olimb, "
          "--assert-audit, --parent-check, --gatelist, --cumulative-item-ceiling or "
          "--gscan.",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
