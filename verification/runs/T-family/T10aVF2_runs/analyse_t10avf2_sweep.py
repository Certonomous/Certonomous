#!/usr/bin/env python3
"""
T10a-VF2 DRIVEN-SWEEP comparator (analyse_t10avf2_sweep.py).

  *** NOT FROZEN. NOT COMMITTED. NO SOLVER RUN, EVER. ***

  This comparator implements the driven-sweep contract of
  docs/campaigns/T-family/T10aVF2_DRIVEN_SWEEP_PREREGISTRATION.md (§2/§3/§4/§5).
  It DECIDES, by measurement, whether the parent's 0.20 signal-to-background
  admissibility constant is NON-LOAD-BEARING (may freeze; VF-3'/VF-6' awarded)
  or LOAD-BEARING (may NOT freeze; VF-3'/VF-6' stay deferred, NOT widened) --
  the V-121 binding condition.

WHAT THIS FILE DOES (cut at freeze; CLAUDE.md rule 2 once frozen):
  * r(case) = B_ctrl(case) / S(case), the per-case admissibility ratio (§2).
  * A(tau) = { case : r(case) <= tau } over the frozen 9-point grid (§3.2).
  * VF-ADM 3-part invariance gate (§3.3): (i) EXACT-GAP CHECK, (ii) A(tau)
    identical across the grid, (iii) VF-3'/VF-6' verdict LABELS identical across
    the grid AND their graded values stable to <= 1e-6 relative. PASS => 0.20
    non-load-bearing. ANY fail => GATE FAIL => VF-3'/VF-6' NOT A RESULT
    (deferred/flagged, not widened; parent §4a, V-121).
  * VF-3' and VF-6' evaluation carried VERBATIM from the prereg §4.
  * TWO rule-3 planted controls (§5): PLANT_ROWSUM (carried; reuses the frozen
    reader) AND PLANT_RATIO (a synthetic in-(0.05,0.25] case that MUST flip
    VF-ADM to GATE FAIL; a detector blind to it REFUSES, exit 2).
  * REFUSES (exit 2) on any missing/stale input; self-hashes its own source;
    a --selftest drives both plants and an AST/logic self-check.

FROZEN READER REUSE (rule 6; §6/§7 of the prereg):
  The predecessor's readers and aggregation are REUSED BY IMPORT from the frozen
  analyse_t10avf2.py (blob ebe19800f0a338664e74f40a89f9c2f35f0d2e05), which is
  READ-ONLY INPUT and is NOT edited or reimplemented here:
      read_boundary, read_faces, stream_list_list, analyse,
      classify_patches, b_ctrl, e_alpha/E_021, check_graded_value_plant.
  The frozen file's blob is asserted at import; a mismatch REFUSES (exit 2).

THE O-1 OPEN QUESTION (verification must rule before freeze):
  The signal S(case) in the ratio is registered PROVISIONALLY as the MIN over the
  case's concave patches of |n_ev * e(0.21)| (S_MODE = "min"). min/max/mean are
  ALL computed and printed so the plant-drive and the eventual O-1 ruling are both
  supported. The freeze selects the ruled mode by flipping the single constant
  S_MODE. Everything downstream of S(case) is S-DEPENDENT -- see the S_DEPENDENT
  manifest printed by --selftest and enumerated in report()["S_DEPENDENT"].

Drafted by a heat-transfer lab-lane, 2026-09-07, zero compute. Freeze and the
§3 supervisor checks are the supervisor's; this file awaits (a) verification's
O-1 S(case) ruling and (b) verification's §3 plant-drive before freeze.
"""
import sys, os, math, json, argparse, hashlib, importlib.util, ast

# ============================================================================
# Import the FROZEN predecessor comparator by explicit path and ASSERT its blob.
# The readers are REUSED, never copied or edited (rule 6).
# ============================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
_AV2_PATH = os.path.normpath(os.path.join(_HERE, "..", "T10aVF_runs", "analyse_t10avf2.py"))
EXPECTED_AV2_BLOB = "ebe19800f0a338664e74f40a89f9c2f35f0d2e05"   # the frozen reader


def git_blob_sha(path):
    """Git blob object sha1 of a file (`git hash-object` equivalent), computed
    WITHOUT invoking git so the integrity check has no external dependency."""
    data = open(path, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def _refuse(msg):
    sys.stderr.write("REFUSE (exit 2): %s\n" % msg)
    sys.exit(2)


def _import_frozen_reader():
    if not os.path.exists(_AV2_PATH):
        _refuse("frozen reader not found at %s" % _AV2_PATH)
    got = git_blob_sha(_AV2_PATH)
    if got != EXPECTED_AV2_BLOB:
        _refuse("frozen reader blob mismatch: got %s expected %s -- the reader "
                "is NOT the frozen ebe19800 file; refusing to reuse it"
                % (got, EXPECTED_AV2_BLOB))
    spec = importlib.util.spec_from_file_location("analyse_t10avf2_frozen", _AV2_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # top-level defs only; main() is __main__-guarded
    return mod


av2 = _import_frozen_reader()             # the frozen reader, imported (never copied)
E_021 = av2.E_021                         # +0.0096524...; the frozen mechanism unit


# ============================================================================
# FROZEN pre-registered constants for THIS arm (pins cut at freeze; rule 2).
# ============================================================================
# --- O-1: the signal mode. PROVISIONAL. The freeze flips this ONE constant. ---
S_MODE = "min"  # PROVISIONAL -- FROZEN AT FREEZE PER VERIFICATION O-1 RULING; do not treat as final

# --- §3.2 the driven grid, §3.3 the exact-gap interval (0.05, 0.25] -----------
TAU_GRID   = [0.05, 0.075, 0.10, 0.125, 0.15, 0.175, 0.20, 0.225, 0.25]
TAU_NOMINAL = 0.20                 # the nominal at which VF-3'/VF-6' are AWARDED on PASS
GAP_LO     = 0.05                  # exact-gap interval is the HALF-OPEN (GAP_LO, GAP_HI]
GAP_HI     = 0.25
VALUE_STABLE_REL = 1e-6            # §3.3(iii) graded-value relative-stability tolerance

# --- §4 VF-3' / VF-6' thresholds, carried VERBATIM from the parent §4 ---------
VF3_EN_LO      = 0.0080            # VF-3'(a) E/n_ev interval, per concave patch
VF3_EN_HI      = 0.0130
VF3_SPREAD_MAX = 0.15             # VF-3'(b) admissible-SPH-level spread ceiling (15%)
VF6_COEFF      = 0.30              # VF-6' band coefficient on B_ctrl
VF6_FLOOR      = 0.003             # VF-6' additive floor

# --- §5 planted-zero controls -------------------------------------------------
PLANT_ROWSUM = av2.PLANT_ROWSUM    # 3.21e-2 -- carried IDENTICAL, via the frozen reader
PLANT_RATIO  = 0.15                # synthetic in-(0.05,0.25] ratio; MUST flip VF-ADM
PLANT_RATIO_TOL = 1e-12

# --- families of S1/S2 (the un-agglomerated geometry the mechanism gates read) -
S1S2_FAMILIES = {"SPH", "BOX", "BALL", "CYL", "SHELL"}
ALPHA_SHIPPED = av2.ALPHA_SHIPPED  # 0.21

# --- self-hash: set by the supervisor AT FREEZE; None => print-only (not frozen) -
EXPECTED_SELF_BLOB = None          # NOT FROZEN YET (rule 2); at freeze set to this file's blob


# ============================================================================
# §2 -- the signal S(case) [O-1 PROVISIONAL] and the ratio r(case).
# EVERYTHING BELOW THIS LINE that consumes r(case) or A(tau) is S-DEPENDENT.
# ============================================================================
def S_case(rec, mode=S_MODE):
    """The case's mechanism SIGNAL, |n_ev * e(0.21)| reduced over the case's
    GRADED (concave, n_ev>0) patches. mode in {"min","max","mean"}.

    O-1 PROVISIONAL: S_MODE="min" is the most conservative (largest ratio,
    hardest admissibility bar); the freeze selects the ruled mode by flipping
    the S_MODE constant only. Returns None if the case has no graded patch
    (caller REFUSES). This function is the single S-choice site."""
    _, graded = av2.classify_patches(rec)
    vals = [abs(rec["patches"][nm]["meanEdgeNbrsVisible"] * E_021) for nm in graded]
    vals = [v for v in vals if v > 0.0]
    if not vals:
        return None
    if mode == "min":
        return min(vals)
    if mode == "max":
        return max(vals)
    if mode == "mean":
        return sum(vals) / len(vals)
    raise ValueError("unknown S_MODE %r (expected min/max/mean)" % (mode,))


def S_case_all(rec):
    """All three S candidates, so the plant-drive and the O-1 ruling are both
    supported (the freeze picks one by flipping S_MODE)."""
    return {m: S_case(rec, m) for m in ("min", "max", "mean")}


def r_case(rec, mode=S_MODE):
    """r(case) = B_ctrl(case) / S(case). B_ctrl from the FROZEN formula (imported
    av2.b_ctrl). Returns None if B_ctrl or S is undefined (caller REFUSES)."""
    bc = av2.b_ctrl(rec)               # frozen: max|E| over n_ev==0 control patches
    S = S_case(rec, mode)
    if bc is None or S is None or S == 0.0:
        return None
    return bc / S


# ============================================================================
# §3 -- the admissible set, the exact-gap check, the τ-sweep.
# ============================================================================
def admissible_set(ratios, tau):
    """A(tau) = { name : r(name) <= tau }.  [S-DEPENDENT via r]"""
    return frozenset(n for n, r in ratios.items() if r is not None and r <= tau)


def exact_gap_check(ratios):
    """§3.3(i) EXACT-GAP CHECK: A(tau) is invariant across [GAP_LO, GAP_HI] IFF
    no case ratio lies in the half-open (GAP_LO, GAP_HI]. Returns
    (ok, [(name, r) in the interval]).  [S-DEPENDENT via r]"""
    in_interval = [(n, r) for n, r in ratios.items()
                   if r is not None and GAP_LO < r <= GAP_HI]
    return (len(in_interval) == 0), in_interval


def sweep_admissible_sets(ratios, grid=TAU_GRID):
    """A(tau) at every grid point.  [S-DEPENDENT]"""
    return {tau: admissible_set(ratios, tau) for tau in grid}


def sets_invariant(sweep):
    """§3.3(ii): A(tau) identical across the whole grid.  [S-DEPENDENT]"""
    vals = list(sweep.values())
    return all(s == vals[0] for s in vals)


# ============================================================================
# §4 -- VF-3' and VF-6', carried VERBATIM. Evaluated on A(tau) => S-DEPENDENT
# via the admissible set (VF-3'(a) alone is S-INDEPENDENT; see manifest).
# ============================================================================
def _meta(rec, key, default=None):
    return rec.get("meta", {}).get(key, default)


def _is_s1s2_graded(rec):
    """S1/S2, un-agglomerated, at the shipped alpha=0.21 (a mechanism-gate case)."""
    return (_meta(rec, "family") in S1S2_FAMILIES
            and int(_meta(rec, "agglomeration", 0)) == 0
            and rec.get("alpha") is not None
            and abs(rec["alpha"] - ALPHA_SHIPPED) < 1e-9)


def eval_vf3(recs, ratios, tau):
    """VF-3' per §4 at threshold tau. Returns (label, values).
      (a) E/n_ev in [VF3_EN_LO, VF3_EN_HI] on EVERY concave patch of S1-S2 at
          alpha=0.21  -- S-INDEPENDENT (does not use tau/A).
      (b) spread of per-level mean concave E/n_ev across the ADMISSIBLE SPH
          levels <= VF3_SPREAD_MAX  -- S-DEPENDENT (uses A(tau)).
    Reduction choice for (b): per SPH level, the representative is the MEAN of
    E/n_ev over that level's concave patches; spread = (max-min)/mean across the
    admissible levels' representatives. (Marked; supervisor confirms at freeze.)"""
    A = admissible_set(ratios, tau)

    # (a) interval on every concave patch of S1/S2 alpha=0.21  [S-INDEPENDENT]
    a_ok = True
    a_worst = None                                    # (name, patch, E/n_ev)
    for n, r in recs.items():
        if not _is_s1s2_graded(r):
            continue
        _, graded = av2.classify_patches(r)
        for nm in graded:
            d = r["patches"][nm]
            nev = d["meanEdgeNbrsVisible"]
            if nev == 0:
                continue
            en = d["meanExcess"] / nev
            inside = VF3_EN_LO <= en <= VF3_EN_HI
            if not inside:
                a_ok = False
            if a_worst is None or abs(en - 0.5 * (VF3_EN_LO + VF3_EN_HI)) > \
                    abs(a_worst[2] - 0.5 * (VF3_EN_LO + VF3_EN_HI)):
                a_worst = (n, nm, en)

    # (b) admissible SPH-level spread  [S-DEPENDENT via A]
    level_reps = {}
    for n, r in recs.items():
        if _meta(r, "family") != "SPH" or _meta(r, "role") != "graded":
            continue
        if int(_meta(r, "agglomeration", 0)) != 0:
            continue
        if n not in A:
            continue
        _, graded = av2.classify_patches(r)
        ens = [r["patches"][nm]["meanExcess"] / r["patches"][nm]["meanEdgeNbrsVisible"]
               for nm in graded if r["patches"][nm]["meanEdgeNbrsVisible"] != 0]
        if ens:
            level_reps[n] = sum(ens) / len(ens)
    if len(level_reps) >= 2:
        vv = list(level_reps.values())
        mean = sum(vv) / len(vv)
        spread = (max(vv) - min(vv)) / mean if mean != 0 else float("inf")
        b_ok = spread <= VF3_SPREAD_MAX
    elif len(level_reps) == 1:
        spread = 0.0
        b_ok = True                                   # a single level cannot spread
    else:
        spread = None
        b_ok = None                                   # no admissible SPH level -> undetermined

    if b_ok is None:
        label = "NOT A RESULT"                        # cannot certify (b) with no admissible level
    else:
        label = "PASS" if (a_ok and b_ok) else "GATE FAIL"
    values = dict(a_ok=a_ok, a_worst=a_worst, b_ok=b_ok, b_spread=spread,
                  admissible_sph_levels=sorted(level_reps.keys()),
                  n_admissible_sph=len(level_reps))
    return label, values


def eval_vf6(recs, ratios, tau):
    """VF-6' per §4 at threshold tau. On every ADMISSIBLE, UN-AGGLOMERATED case:
    every patch mean of the alpha=exp(-3/2) twin satisfies
        |E_afix - B_ctrl(case)| <= max(VF6_COEFF*B_ctrl(case), VF6_FLOOR).
    Returns (label, values).  [S-DEPENDENT via A]
    Twin resolution: meta['twin'] if present, else name+"_afix" if present."""
    A = admissible_set(ratios, tau)
    worst = None                                      # (case, patch, margin)
    n_graded = 0
    all_ok = True
    for n, r in recs.items():
        if n not in A:
            continue
        if not (_meta(r, "family") in S1S2_FAMILIES
                and int(_meta(r, "agglomeration", 0)) == 0
                and r.get("alpha") is not None
                and abs(r["alpha"] - ALPHA_SHIPPED) < 1e-9):
            continue
        bc = av2.b_ctrl(r)
        if bc is None:
            return "NOT A RESULT", dict(reason="admissible case %s has no B_ctrl" % n)
        twin = _meta(r, "twin") or (n + "_afix")
        if twin not in recs:
            return "NOT A RESULT", dict(reason="afix twin %s of %s absent" % (twin, n))
        tw = recs[twin]
        band = max(VF6_COEFF * bc, VF6_FLOOR)
        for nm, d in tw["patches"].items():
            n_graded += 1
            e_afix = d["meanExcess"]
            margin = abs(e_afix - bc) - band            # <= 0 means inside
            if margin > 0:
                all_ok = False
            if worst is None or margin > worst[2]:
                worst = (n, nm, margin)
    if n_graded == 0:
        return "NOT A RESULT", dict(reason="no admissible un-agglomerated case")
    return ("PASS" if all_ok else "GATE FAIL"), dict(worst=worst, n_patches=n_graded)


def _value_signature(vf3_vals, vf6_vals):
    """Numeric fingerprint of the graded values VF-3'/VF-6' compute at one tau,
    for the §3.3(iii) relative-stability comparison across the grid."""
    sig = []
    for v in (vf3_vals.get("b_spread"),
              (vf3_vals.get("a_worst") or (None, None, None))[2]):
        sig.append(float("nan") if v is None else float(v))
    w = vf6_vals.get("worst")
    sig.append(float("nan") if not w else float(w[2]))
    return sig


def _sig_stable(sigs, rel=VALUE_STABLE_REL):
    """True iff every component is stable to <= rel relative across the grid
    (NaNs must match position-for-position -- an undetermined value is stable
    only if undetermined everywhere)."""
    if not sigs:
        return True
    ref = sigs[0]
    for s in sigs[1:]:
        if len(s) != len(ref):
            return False
        for a, b in zip(ref, s):
            an, bn = math.isnan(a), math.isnan(b)
            if an != bn:
                return False
            if an and bn:
                continue
            denom = max(abs(a), abs(b), 1e-300)
            if abs(a - b) / denom > rel:
                return False
    return True


# ============================================================================
# §3.3 -- the VF-ADM invariance gate. The load-bearing decision of this arm.
# `gap_checker` is injectable ONLY so the §5 ratio-plant can prove the detector
# is NOT blind to an in-range case (default is the real exact_gap_check).
# ============================================================================
def vf_adm(recs, ratios, grid=TAU_GRID, gap_checker=exact_gap_check):
    """VF-ADM (§3.3). PASS iff all three hold:
      (i) exact-gap check passes (no r in (GAP_LO, GAP_HI]);
      (ii) A(tau) identical across the grid;
      (iii) VF-3' and VF-6' verdict LABELS identical across the grid AND their
            graded values stable to <= VALUE_STABLE_REL relative.
    ANY failure => GATE FAIL (0.20 declared LOAD-BEARING; VF-3'/VF-6' NOT A
    RESULT, deferred/flagged, NOT widened -- parent §4a, V-121).  [S-DEPENDENT]"""
    gap_ok, in_interval = gap_checker(ratios)
    sweep = sweep_admissible_sets(ratios, grid)
    sets_ok = sets_invariant(sweep)

    vf3_labels, vf6_labels, sigs = [], [], []
    per_tau = {}
    for tau in grid:
        l3, v3 = eval_vf3(recs, ratios, tau)
        l6, v6 = eval_vf6(recs, ratios, tau)
        vf3_labels.append(l3)
        vf6_labels.append(l6)
        sigs.append(_value_signature(v3, v6))
        per_tau[tau] = dict(vf3=l3, vf6=l6, A=sorted(sweep[tau]))
    labels_ok = (len(set(vf3_labels)) == 1 and len(set(vf6_labels)) == 1)
    values_ok = _sig_stable(sigs)
    part_iii = labels_ok and values_ok

    verdict = "PASS" if (gap_ok and sets_ok and part_iii) else "GATE FAIL"
    detail = dict(
        verdict=verdict,
        part_i_exact_gap=dict(ok=gap_ok, ratios_in_interval=in_interval),
        part_ii_sets_invariant=dict(ok=sets_ok,
                                    n_distinct_sets=len({frozenset(s) for s in sweep.values()})),
        part_iii_dependent_verdicts=dict(ok=part_iii, labels_ok=labels_ok,
                                         values_ok=values_ok,
                                         vf3_labels=vf3_labels, vf6_labels=vf6_labels),
        per_tau=per_tau,
        consequence=("0.20 NON-LOAD-BEARING: may freeze; VF-3'/VF-6' AWARDED at "
                     "tau=%.2f" % TAU_NOMINAL if verdict == "PASS"
                     else "0.20 LOAD-BEARING: VF-3'/VF-6' -> NOT A RESULT, "
                          "deferred/not-widened (parent §4a, V-121)"))
    return verdict, detail


# ============================================================================
# §5.2 -- the ratio-partition planted control (NEW, load-bearing for VF-ADM).
# ============================================================================
def check_ratio_partition_plant(recs, ratios, detector=None):
    """§5.2. The invariance detector must be shown able to SEE a load-bearing
    (in-range) ratio, or a PASS from it is not evidence.
      RED : inject one synthetic case with r = PLANT_RATIO (in (GAP_LO, GAP_HI])
            -> the detector MUST return VF-ADM GATE FAIL.
      GREEN: the clean set (synthetic case removed) -> the detector returns its
             real verdict (non-vacuity twin).
    ok = the RED case is caught (GATE FAIL). A detector that stays non-GATE-FAIL
    on the planted in-range ratio is BLIND -> ok=False -> caller REFUSES (exit 2)
    (rule 3). `detector(recs, ratios) -> (verdict, detail)`; default vf_adm."""
    if not (GAP_LO < PLANT_RATIO <= GAP_HI):
        return dict(ok=False, reason="PLANT_RATIO %.4f not in the (%.3f,%.3f] "
                    "load-bearing interval -- plant is vacuous"
                    % (PLANT_RATIO, GAP_LO, GAP_HI))
    detector = detector or vf_adm
    PKEY = "__PLANT_RATIO_SYNTHETIC__"
    # A synthetic rec that carries no graded/afix meta -> VF-3'/VF-6' ignore it;
    # only its ratio enters, tripping the exact-gap check and A(tau) invariance.
    synth_rec = dict(patches={}, comp=[], alpha=None, meta={"role": "__plant__"})
    pert_recs = dict(recs); pert_recs[PKEY] = synth_rec
    pert_ratios = dict(ratios); pert_ratios[PKEY] = PLANT_RATIO

    red_verdict, red_detail = detector(pert_recs, pert_ratios)          # RED
    green_verdict, _ = detector(dict(recs), dict(ratios))               # GREEN

    red_ok = (red_verdict == "GATE FAIL")
    # non-vacuity: the planted ratio must actually be reported inside the interval
    in_iv = red_detail.get("part_i_exact_gap", {}).get("ratios_in_interval", [])
    saw_plant = any(abs(r - PLANT_RATIO) <= PLANT_RATIO_TOL for _, r in in_iv)
    ok = red_ok and saw_plant
    return dict(ok=ok, red_verdict=red_verdict, green_verdict=green_verdict,
                saw_planted_ratio=saw_plant, plant=PLANT_RATIO,
                reason=None if ok else ("detector BLIND to an in-range ratio "
                                        "(red_verdict=%s, saw_plant=%s)"
                                        % (red_verdict, saw_plant)))


# ============================================================================
# Self-hash and AST/logic self-check.
# ============================================================================
def self_source_blob():
    return git_blob_sha(os.path.abspath(__file__))


def ast_self_check():
    """Logic self-check (rule 6 / rule 3 evidence): PROVE this file REUSES the
    frozen reader by import rather than copying it, and that the O-1 provisional
    is present. Returns (ok, [messages])."""
    msgs = []
    src = open(os.path.abspath(__file__)).read()
    tree = ast.parse(src)

    # 1) The frozen readers must NOT be redefined here (proof of import-reuse).
    copied = {"read_boundary", "read_faces", "stream_list_list", "analyse",
              "classify_patches", "b_ctrl", "e_alpha"}
    defs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    reimplemented = copied & defs
    if reimplemented:
        msgs.append("FAIL: reimplements frozen reader(s): %s" % sorted(reimplemented))

    # 2) The frozen module must never be monkeypatched (no `av2.<x> = ...`).
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) \
                        and t.value.id == "av2":
                    msgs.append("FAIL: assigns to frozen module av2.%s" % t.attr)

    # 3) The import-by-path of the frozen reader must be present.
    if "analyse_t10avf2.py" not in src or "spec_from_file_location" not in src:
        msgs.append("FAIL: no import-by-path of the frozen analyse_t10avf2.py")

    # 4) The blob assertion must be present.
    if EXPECTED_AV2_BLOB not in src:
        msgs.append("FAIL: frozen-blob assertion missing")

    # 5) O-1: S_MODE assigned the provisional string with the freeze marker.
    smode_ok = any(isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "S_MODE" for t in n.targets)
                   and isinstance(n.value, ast.Constant) and n.value.value == "min"
                   for n in ast.walk(tree))
    if not (smode_ok and "FROZEN AT FREEZE PER VERIFICATION O-1 RULING" in src):
        msgs.append("FAIL: S_MODE provisional/O-1 marker not intact")

    return (len(msgs) == 0), msgs


# ============================================================================
# The S-DEPENDENT manifest -- what changes with the S_MODE (O-1) choice.
# ============================================================================
S_DEPENDENT = [
    "S_case (the signal itself; the single O-1 choice site)",
    "r_case = B_ctrl / S",
    "admissible_set A(tau)",
    "exact_gap_check (part i)",
    "sweep_admissible_sets / sets_invariant (part ii)",
    "eval_vf3 part (b) -- admissible-SPH-level spread (part (a) is S-INDEPENDENT)",
    "eval_vf6 -- graded over the admissible un-agglomerated set",
    "vf_adm verdict (via i/ii/iii)",
    "which cases VF-3'/VF-6' are awarded on at tau=TAU_NOMINAL (part iii)",
]
S_INDEPENDENT = [
    "B_ctrl(case) (frozen formula; the ratio numerator)",
    "VF-3' part (a): E/n_ev in [0.0080,0.0130] over ALL S1/S2 concave patches",
    "the §5 row-sum plant (PLANT_ROWSUM), via the frozen reader",
    "the §5 ratio plant is by construction in-range for any S_MODE",
]


# ============================================================================
# --selftest -- synthetic/planted fixtures only. NO SOLVER RUN.
# ============================================================================
def _mk_rec(name, control_excess, graded_specs, meta):
    """Build a synthetic analyse()-shaped record. control_excess: list of
    meanExcess for n_ev==0 control patches. graded_specs: list of (n_ev, E) for
    concave patches (n_ev>0). meta: CASE.json-like dict."""
    patches = {}
    comp = []
    idx = 0
    for i, ex in enumerate(control_excess):
        nm = "%s_ctrl%d" % (name, i)
        patches[nm] = dict(nEdgeVisSum=0, meanExcess=ex, meanEdgeNbrsVisible=0.0,
                           meanRowSum=1.0 + ex)
        comp.append([nm, idx, idx + 1, idx]); idx += 1
    for i, (nev, E) in enumerate(graded_specs):
        nm = "%s_g%d" % (name, i)
        patches[nm] = dict(nEdgeVisSum=int(round(nev)), meanExcess=E,
                           meanEdgeNbrsVisible=float(nev), meanRowSum=1.0 + E)
        comp.append([nm, idx, idx + 1, idx]); idx += 1
    return dict(case=name, patches=patches, comp=comp, meta=meta,
                alpha=meta.get("alpha"))


def run_selftest():
    fails = []
    print("=== analyse_t10avf2_sweep.py --selftest (synthetic fixtures, NO SOLVER) ===")
    print("frozen reader %s blob=%s (expected %s)"
          % (_AV2_PATH, git_blob_sha(_AV2_PATH), EXPECTED_AV2_BLOB))
    print("this file blob=%s  (EXPECTED_SELF_BLOB=%s -- %s)"
          % (self_source_blob(), EXPECTED_SELF_BLOB,
             "NOT FROZEN, print-only" if EXPECTED_SELF_BLOB is None else "asserted"))

    # ---- Build a clean synthetic family whose ratios straddle the gap ---------
    # SPH levels admissible (r≈0.03 <= 0.05); an inadmissible high-N case (r≈0.31 > 0.25).
    # Graded E chosen so E/n_ev = 0.0100 (inside VF-3'(a) [0.0080,0.0130]).
    EN = 0.0100
    recs = {}
    # 3 admissible SPH graded levels + their afix twins (E_afix ~ B_ctrl -> VF-6' PASS)
    for lv, nev in (("L2", 40.0), ("L3", 60.0), ("L4", 80.0)):
        nm = "SPH_%s" % lv
        bc = 0.03 * abs(nev * E_021)                 # r = bc/(min|nev*e|) = 0.03
        recs[nm] = _mk_rec(nm, [bc, 0.5 * bc], [(nev, EN * nev)],
                           dict(family="SPH", role="graded", alpha=ALPHA_SHIPPED,
                                agglomeration=0, twin=nm + "_afix"))
        # afix twin: mechanism removed -> patch excess ~ B_ctrl (inside VF-6' band)
        recs[nm + "_afix"] = _mk_rec(nm + "_afix", [bc, 0.5 * bc],
                                     [(nev, bc)],
                                     dict(family="SPH", role="afix",
                                          alpha=av2.ALPHA_FIX, agglomeration=0))
    # one inadmissible high-N SPH level (r≈0.31), NOT in A -> excluded from VF-3'(b)
    hb = 0.31 * abs(8.0 * E_021)
    recs["SPH_L1"] = _mk_rec("SPH_L1", [hb], [(8.0, EN * 8.0)],
                             dict(family="SPH", role="graded", alpha=ALPHA_SHIPPED,
                                  agglomeration=0, twin="SPH_L1_afix"))
    recs["SPH_L1_afix"] = _mk_rec("SPH_L1_afix", [hb], [(8.0, hb)],
                                  dict(family="SPH", role="afix",
                                       alpha=av2.ALPHA_FIX, agglomeration=0))

    ratios = {n: r_case(r) for n, r in recs.items()}
    ratios = {n: v for n, v in ratios.items() if v is not None}

    # [A] S candidates printed (O-1 support): min/max/mean per graded case
    print("\n[A] S(case) candidates (O-1: freeze picks min/max/mean via S_MODE); "
          "S_MODE=%r" % S_MODE)
    for n in sorted(recs):
        if av2.classify_patches(recs[n])[1]:
            sc = S_case_all(recs[n])
            print("    %-14s S: min=%.6e max=%.6e mean=%.6e  r(min)=%s"
                  % (n, sc["min"], sc["max"], sc["mean"],
                     ("%.4f" % r_case(recs[n], "min")) if r_case(recs[n], "min") else "None"))

    # [B] VF-ADM PASS on the clean straddling family (all r<=0.05 or >0.25)
    v_clean, d_clean = vf_adm(recs, ratios)
    gap_ok = d_clean["part_i_exact_gap"]["ok"]
    clean_pass = (v_clean == "PASS")
    print("\n[B] clean family VF-ADM: %s  (gap_ok=%s, sets_invariant=%s, part_iii=%s)"
          % (v_clean, gap_ok, d_clean["part_ii_sets_invariant"]["ok"],
             d_clean["part_iii_dependent_verdicts"]["ok"]))
    print("    VF-3' labels across grid: %s" % d_clean["part_iii_dependent_verdicts"]["vf3_labels"])
    print("    VF-6' labels across grid: %s" % d_clean["part_iii_dependent_verdicts"]["vf6_labels"])
    if not clean_pass:
        fails.append("[B] clean straddling family did not VF-ADM PASS (v=%s)" % v_clean)

    # ---- PLANT 1: §5.1 row-sum plant via the FROZEN reader --------------------
    import tempfile, shutil
    tmp = tempfile.mkdtemp(prefix="t10avf2_sweep_selftest_")
    try:
        case = os.path.join(tmp, "synthetic_case")
        os.makedirs(os.path.join(case, "constant"))
        av2._make_listlist_file(os.path.join(case, "constant", "F"),
                                [[0.10, 0.20, 0.30], [0.40, 0.60], [0.55, 0.45]])
        pr = av2.check_graded_value_plant(case, os.path.join(case, "_plant_scratch"))
        good = pr["ok"] and pr["red_ok"] and pr["green_ok"] \
            and abs(pr["rose"] - PLANT_ROWSUM) <= av2.PLANT_TOL
        print("\n[P1a] row-sum plant fires via FROZEN reader (RED seen, GREEN clean): "
              "%s  rose=%.6e (plant=%.6e)"
              % ("PASS" if good else "FAIL", pr["rose"], PLANT_ROWSUM))
        if not good:
            fails.append("[P1a] row-sum plant did not fire")
        blind = av2.check_graded_value_plant(case, os.path.join(case, "_plant_scratch2"),
                                             reader=lambda p, f: 0.0)
        caught = (not blind["ok"]) and (not blind["red_ok"])
        print("[P1b] BLIND row-sum reader caught (refuses, exit-2 path): %s"
              % ("PASS" if caught else "FAIL"))
        if not caught:
            fails.append("[P1b] blind row-sum reader not caught")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- PLANT 2: §5.2 ratio-partition plant flips VF-ADM to GATE FAIL --------
    rp = check_ratio_partition_plant(recs, ratios)
    p2_red = (rp["ok"] and rp["red_verdict"] == "GATE FAIL" and rp["saw_planted_ratio"])
    print("\n[P2a] ratio plant (r=%.2f in (%.2f,%.2f]) flips VF-ADM to GATE FAIL: %s "
          "(red=%s, green=%s, saw_plant=%s)"
          % (PLANT_RATIO, GAP_LO, GAP_HI, "PASS" if p2_red else "FAIL",
             rp["red_verdict"], rp["green_verdict"], rp["saw_planted_ratio"]))
    if not p2_red:
        fails.append("[P2a] ratio plant did not flip VF-ADM to GATE FAIL")

    # BLIND detector: an invariance gate whose gap-check ignores in-range ratios.
    def blind_gap(ratios_):                       # sees no in-range case, ever
        return True, []
    def blind_detector(recs_, ratios_):
        return vf_adm(recs_, ratios_, gap_checker=blind_gap)
    rp_blind = check_ratio_partition_plant(recs, ratios, detector=blind_detector)
    p2_blind = (not rp_blind["ok"])               # a blind detector MUST be caught
    print("[P2b] BLIND invariance detector caught (plant refuses, exit-2 path): %s "
          "(blind red_verdict=%s)"
          % ("PASS" if p2_blind else "FAIL", rp_blind["red_verdict"]))
    if not p2_blind:
        fails.append("[P2b] blind invariance detector not caught")

    # ---- AST/logic self-check --------------------------------------------------
    ok_ast, ast_msgs = ast_self_check()
    print("\n[AST] import-reuse / no-monkeypatch / O-1-marker self-check: %s%s"
          % ("PASS" if ok_ast else "FAIL", "" if ok_ast else "  -> " + "; ".join(ast_msgs)))
    if not ok_ast:
        fails.append("[AST] " + "; ".join(ast_msgs))

    # ---- S-DEPENDENT manifest --------------------------------------------------
    print("\n[S-DEPENDENT computations (change with the S_MODE / O-1 choice):]")
    for s in S_DEPENDENT:
        print("    - " + s)
    print("[S-INDEPENDENT:]")
    for s in S_INDEPENDENT:
        print("    - " + s)

    print("\n=== SELFTEST %s ==="
          % ("PASS (rc 0)" if not fails else "FAIL (rc 1): " + "; ".join(fails)))
    return 0 if not fails else 1


# ============================================================================
# Real-case driver. REFUSES (exit 2) on any missing/stale input (rule 4; §6).
# NO SOLVER RUN. Reads viewFactorsGen outputs the parent VF-4' arm defines.
# ============================================================================
def _age_guard(case):
    """§6 age guard, viewFactorsGen flavour: if the case carries its own 0/T,
    constant/F must be NEWER than it (the answer post-dates launch). Refuses on a
    stale field. viewFactorsGen-only cases without 0/T are unconstrained here."""
    t0 = os.path.join(case, "0", "T")
    F = os.path.join(case, "constant", "F")
    if os.path.exists(t0) and os.path.exists(F):
        if os.path.getmtime(F) <= os.path.getmtime(t0):
            _refuse("age guard: %s not newer than %s (stale input)" % (F, t0))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cases", nargs="*", help="case directories to grade")
    ap.add_argument("--out", default=None, help="write combined JSON here")
    ap.add_argument("--selftest", action="store_true",
                    help="drive both plants + the AST/logic self-check; NO SOLVER")
    a = ap.parse_args()

    # Self-hash: print always; assert only once frozen (EXPECTED_SELF_BLOB set).
    my_blob = self_source_blob()
    if EXPECTED_SELF_BLOB is not None and my_blob != EXPECTED_SELF_BLOB:
        _refuse("comparator self-hash mismatch: got %s expected %s (not the frozen file)"
                % (my_blob, EXPECTED_SELF_BLOB))

    if a.selftest:
        sys.exit(run_selftest())

    if not a.cases:
        _refuse("no cases given and --selftest not set")

    # Build records via the FROZEN analyse(); refuse on any missing/stale input.
    recs = {}
    for c in a.cases:
        if not os.path.isdir(c):
            _refuse("case dir missing: %s" % c)
        _age_guard(c)
        try:
            r = av2.analyse(c)
        except Exception as e:
            _refuse("frozen analyse() failed on %s: %s" % (c, e))
        recs[os.path.basename(os.path.abspath(c))] = r

    # §5.1 row-sum plant on every case (refuse if the reader is blind to it).
    plant1 = {}
    for n, r in recs.items():
        pr = av2.check_graded_value_plant(r["case"], os.path.join(r["case"], "_plant_scratch"))
        plant1[n] = pr
        if not pr["ok"]:
            _refuse("row-sum plant not recovered on %s: %s" % (n, pr["reason"]))

    # Ratios (S-DEPENDENT). Refuse a graded case whose ratio is undefined.
    ratios, s_all = {}, {}
    for n, r in recs.items():
        _, graded = av2.classify_patches(r)
        if not graded:
            continue                                  # pure-control/utility case: no ratio
        rr = r_case(r)
        if rr is None:
            _refuse("ratio undefined for %s (no B_ctrl or S)" % n)
        ratios[n] = rr
        s_all[n] = S_case_all(r)

    if not ratios:
        _refuse("no case yielded a graded ratio; nothing to sweep")

    # §5.2 ratio-partition plant: prove the detector can SEE a load-bearing case.
    rp = check_ratio_partition_plant(recs, ratios)
    if not rp["ok"]:
        _refuse("ratio-partition plant did not flip VF-ADM (detector blind): %s" % rp["reason"])

    # VF-ADM across the grid (the load-bearing decision).
    v_adm, d_adm = vf_adm(recs, ratios)

    # VF-3'/VF-6' at the nominal tau -- AWARDED only if VF-ADM PASS; else NOT A RESULT.
    l3, val3 = eval_vf3(recs, ratios, TAU_NOMINAL)
    l6, val6 = eval_vf6(recs, ratios, TAU_NOMINAL)
    if v_adm != "PASS":
        vf3_final, vf6_final = "NOT A RESULT", "NOT A RESULT"
    else:
        vf3_final, vf6_final = l3, l6

    report = dict(
        arm="T10a-VF2 driven-sweep",
        S_MODE=S_MODE, S_MODE_note="PROVISIONAL -- O-1 ruling pending",
        S_candidates=s_all, tau_grid=TAU_GRID, tau_nominal=TAU_NOMINAL,
        ratios=ratios,
        gates=dict(
            VF_ADM=d_adm,
            VF_3prime=dict(verdict=vf3_final, at_nominal=l3, values=val3),
            VF_6prime=dict(verdict=vf6_final, at_nominal=l6, values=val6),
        ),
        planted_zero_controls=dict(row_sum=plant1, ratio_partition=rp),
        S_DEPENDENT=S_DEPENDENT, S_INDEPENDENT=S_INDEPENDENT,
        self_blob=my_blob, frozen_reader_blob=git_blob_sha(_AV2_PATH),
    )

    print("VF-ADM (0.20 non-load-bearing?): %s" % v_adm)
    print("  %s" % d_adm["consequence"])
    print("  part i  exact-gap : %s  (ratios in (%.2f,%.2f]: %s)"
          % (d_adm["part_i_exact_gap"]["ok"], GAP_LO, GAP_HI,
             d_adm["part_i_exact_gap"]["ratios_in_interval"]))
    print("  part ii A(tau)    : %s" % d_adm["part_ii_sets_invariant"]["ok"])
    print("  part iii verdicts : %s" % d_adm["part_iii_dependent_verdicts"]["ok"])
    print("VF-3': %s   VF-6': %s   (awarded only on VF-ADM PASS)" % (vf3_final, vf6_final))

    if a.out:
        json.dump(report, open(a.out, "w"), indent=1, default=str)
        print("wrote %s" % os.path.abspath(a.out))


if __name__ == "__main__":
    main()
