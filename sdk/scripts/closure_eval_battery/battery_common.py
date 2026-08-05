"""Shared machinery for the closure-challenge evaluation battery.

PURPOSE. The challenge reduces every submission to one number per case
(scaled MAE of the velocity vector at 1000 points). The literature the
entrants and the benchmark itself descend from judges models on richer
diagnostics: velocity profiles at standard stations, 1:1 scatter against
truth, spatial error maps, and (for ducts) in-plane secondary-flow
structure. This package implements that battery ON TRAINING/VALIDATION
DATA ONLY, where reading ground truth is legal under the benchmark's own
split. Census and per-metric citations:
demo-output/website/CLOSURE_EVALUATION_PROTOCOL.md.

TEST-BLINDNESS, ENFORCED TWICE:
  1. The raising-stub scoring guard (same pattern as
     sdk/scripts/closure_divergence_audit.py) is armed before any work:
     every closure_challenge function that can reach test ground-truth
     velocities raises. No scoring call can happen in these processes.
  2. Every ground-truth loader in this module asserts its case against a
     TRAIN/VALIDATION whitelist before opening any file. Test cases
     cannot have their truth read even by a future editing mistake,
     because the whitelist is checked in the loader itself.

MODELS. Exactly the entry of record (round 4):
  * PH model  -- round-1 HistGradientBoostingRegressor x3 components,
    max_iter=300, max_depth=6, lr=0.05, l2=1.0, random_state=0, trained
    on the 21 PH training cases, 7 Pope-invariant features.
    Validity anchor: validation pooled scaled MAE must equal the recorded
    0.0876 (closure_challenge_trained_entry.json, quoted in
    closure_challenge_stability_physicality_audit.md §1).
  * DUCT model -- round-4 "variant D": 8th feature d/d_max, target
    (U_LES-U_RANS)/mean|U_RANS|, same estimator/HP, trained on the 4
    suggested DUCT training cases.
    Validity anchor: AR_7_Ret_180 validation scaled MAE must equal the
    pre-registered 0.01345 (closure_challenge_duct_reynolds_transfer.json).

STYLE (fixed for the whole battery; see protocol doc §5 for the
literature precedent): truth = black filled circles, RANS baseline =
blue (#0077BB) dashed line, our corrected field = red (#CC3311) solid
line. Magnitude maps use viridis with a shared colorbar per figure.
Every axes title states the population and the averaging convention
(lab rule: katie-gui-conventions).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_SCRIPTS = _HERE.parent          # sdk/scripts
_REPO = _SCRIPTS.parent.parent   # repo root
sys.path.insert(0, str(_SCRIPTS))

import train_closure_periodic_hill_correction as ph  # noqa: E402
import train_closure_extended_correction as ex       # noqa: E402

OUT_DIR = _REPO / "demo-output" / "website" / "closure_eval"

# ---------------------------------------------------------------------------
# Fixed battery style (entity -> color, never re-assigned; pair validated
# CVD-safe: worst adjacent deltaE 10.3 protan, normal-vision 26.9, both pass)
# ---------------------------------------------------------------------------
C_TRUTH = "black"     # truth: black FILLED CIRCLES (markers, not a line)
C_RANS = "#0077BB"    # RANS baseline: blue DASHED line
C_CORR = "#CC3311"    # our corrected field: red SOLID line
CMAP_MAG = "viridis"  # sequential magnitude maps

TRUTH_KW = dict(color=C_TRUTH, marker="o", linestyle="none",
                markersize=3.5, zorder=5, label="truth (LES/DNS)")
RANS_KW = dict(color=C_RANS, linestyle="--", linewidth=1.6,
               zorder=3, label="RANS baseline (k-ω SST)")
CORR_KW = dict(color=C_CORR, linestyle="-", linewidth=1.6,
               zorder=4, label="corrected (entry of record)")

HP = dict(max_iter=300, max_depth=6, learning_rate=0.05,
          l2_regularization=1.0, random_state=0)

# ---------------------------------------------------------------------------
# Whitelists: the ONLY cases whose ground truth these loaders will open.
# ---------------------------------------------------------------------------
PH_TRUTH_LEGAL = set(ph._PH_TRAIN) | set(ph._PH_VAL)
DUCT_TRUTH_LEGAL = set(ex._DUCT_TRAIN) | set(ex._DUCT_VAL)


class ScoringCallRefused(RuntimeError):
    pass


def arm_scoring_guard():
    """Import the evaluation package solely to disable it, then prove the
    guard is armed. Identical raising-stub pattern to
    closure_divergence_audit.py; nothing in the battery may score."""
    if str(ph.EVAL_PKG_DIR / "src") not in sys.path:
        sys.path.insert(0, str(ph.EVAL_PKG_DIR / "src"))
    import closure_challenge as _cc
    from closure_challenge import dataset_utils as _du
    from closure_challenge import eval as _ev

    def _refuse(name):
        def _raiser(*_a, **_kw):
            raise ScoringCallRefused(
                f"{name}() was called from the closure evaluation battery. "
                "The battery is test-blind by construction: no scoring call, "
                "no test ground-truth read, ever.")
        return _raiser

    blocked = ("score", "score_from_csv", "evaluate_by_case",
               "evaluate_from_csv_by_case", "evaluate_individual_case",
               "_velocity_field", "_ground_truth", "_load_csv_predictions",
               "evaluation_points")
    for mod in (_cc, _du, _ev):
        for name in blocked:
            if hasattr(mod, name):
                setattr(mod, name, _refuse(name))
    try:
        _cc.score({})
    except ScoringCallRefused:
        print("[guard] verified: closure_challenge.score() now raises")
    else:  # pragma: no cover
        raise SystemExit("scoring guard failed to arm; refusing to continue")


# ---------------------------------------------------------------------------
# Field + truth loading (whitelisted)
# ---------------------------------------------------------------------------
def load_ph_case(case: str, parse_internal_field, with_truth: bool):
    f = ph._load_rans_fields(case, parse_internal_field)
    if with_truth:
        assert case in PH_TRUTH_LEGAL, (
            f"REFUSED: {case} is not a PH train/validation case; "
            "its ground truth is test data.")
        f["U_truth"] = ph._load_ground_truth_U(case, parse_internal_field)
    return f


def load_duct_case(case: str, parse_internal_field, with_truth: bool):
    f = ex._reconstruct_duct_fields(case, parse_internal_field)
    if with_truth:
        assert case in DUCT_TRUTH_LEGAL, (
            f"REFUSED: {case} is not a DUCT train/validation case; "
            "its ground truth is test data.")
        f["U_truth"] = ex._load_duct_ground_truth_U(case, parse_internal_field)
    return f


# ---------------------------------------------------------------------------
# Model refits (byte-identical recipes to the entry of record)
# ---------------------------------------------------------------------------
def fit_ph_model(parse_internal_field):
    """Round-1 PH model, random_state=0. Returns predict(X)->(n,3) dU."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    Xs, Ys = [], []
    for c in ph._PH_TRAIN:
        f = load_ph_case(c, parse_internal_field, with_truth=True)
        Xs.append(ph.build_features(f["gradU"], f["k"], f["omega"],
                                    f["walldist"], f["U"], f["nu"]))
        Ys.append(f["U_truth"] - f["U"])
    X = np.concatenate(Xs)
    Y = np.concatenate(Ys)
    models = [HistGradientBoostingRegressor(**HP).fit(X, Y[:, j]) for j in range(3)]
    return lambda Xq: np.stack([m.predict(Xq) for m in models], axis=1)


def duct_features(f):
    """Variant D features: the 7 Pope invariants + d/d_max (round-4 recipe)."""
    X7 = ph.build_features(f["gradU"], f["k"], f["omega"],
                           f["walldist"], f["U"], f["nu"])
    d = f["walldist"]
    return np.hstack([X7, (d / d.max())[:, None]])


def fit_duct_model(parse_internal_field):
    """Round-4 variant D. Returns predict(f)->(n,3) dU (already rescaled)."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    Xs, Ys = [], []
    for c in ex._DUCT_TRAIN:
        f = load_duct_case(c, parse_internal_field, with_truth=True)
        uref = float(np.linalg.norm(f["U"], axis=1).mean())
        Xs.append(duct_features(f))
        Ys.append((f["U_truth"] - f["U"]) / uref)
    X = np.concatenate(Xs)
    Y = np.concatenate(Ys)
    models = [HistGradientBoostingRegressor(**HP).fit(X, Y[:, j]) for j in range(3)]

    def predict(f):
        uref = float(np.linalg.norm(f["U"], axis=1).mean())
        return np.column_stack([m.predict(duct_features(f)) for m in models]) * uref
    return predict


# ---------------------------------------------------------------------------
# Metrics (cell-population form of the challenge metric, + pointwise map)
# ---------------------------------------------------------------------------
def scaled_mae_cells(U_pred, U_true):
    """The challenge's scaled MAE evaluated on ALL mesh cells instead of
    the 1000 official points: mean ||U_pred-U_true||_2 / mean ||U_true||_2.
    Same formula as closure_challenge.eval.evaluate_individual_case."""
    return float(np.mean(np.linalg.norm(U_pred - U_true, axis=-1))
                 / np.mean(np.linalg.norm(U_true, axis=-1)))


def pointwise_error(U_pred, U_true):
    """||U_pred - U_true||_2 per cell -- the integrand of the challenge
    metric, plottable as a map."""
    return np.linalg.norm(U_pred - U_true, axis=-1)


# ---------------------------------------------------------------------------
# Periodic-hill geometry helpers
# ---------------------------------------------------------------------------
def ph_geometry(C):
    """Hill height h and domain size, measured from the mesh's own cell
    centres -- not assumed.

    h is the maximum of the lower-boundary curve, i.e. the crest height.
    The case-name suffix independently encodes the domain height in crest
    units (2024 -> Ly/h ~ 2.024, 3036 -> ~3.036 = Breuer's channel height,
    4048 -> ~4.048); run_ph_battery.py checks the measured Ly/h against
    that tag before trusting either, so the normalisation is verified from
    two independent sources."""
    x, y = C[:, 0], C[:, 1]
    Lx = float(x.max())
    Ly = float(y.max())
    # lower boundary curve floor(x): min cell-centre y in 80 x-bins
    bins = np.linspace(0.0, Lx, 81)
    idx = np.clip(np.digitize(x, bins) - 1, 0, 79)
    floor = np.full(80, np.nan)
    for b in range(80):
        m = idx == b
        if m.any():
            floor[b] = y[m].min()
    xc = 0.5 * (bins[:-1] + bins[1:])
    h = float(np.nanmax(floor))
    return dict(Lx=Lx, Ly=Ly, h=h, floor_x=xc, floor_y=floor)


def sample_profile(C, F, x0, y_lo, y_hi, n=60):
    """Linear-interpolate scalar field F onto the vertical line x=x0,
    y in [y_lo, y_hi]. Returns (y, values)."""
    from scipy.interpolate import griddata
    ys = np.linspace(y_lo, y_hi, n)
    pts = np.column_stack([np.full(n, x0), ys])
    vals = griddata(C[:, :2], F, pts, method="linear")
    # linear griddata returns NaN outside the convex hull (near curved
    # walls); fall back to nearest there so profiles reach the wall
    bad = ~np.isfinite(vals)
    if bad.any():
        vals[bad] = griddata(C[:, :2], F, pts[bad], method="nearest")
    return ys, vals


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path}")
