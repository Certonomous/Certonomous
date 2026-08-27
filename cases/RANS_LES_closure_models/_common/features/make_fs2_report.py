#!/usr/bin/env python3
"""Render FS2_DEGENERACY_REPORT.md from fs2_audit.json + invariance_check.json.
Generated: re-running reproduces it."""
from __future__ import annotations
import copy, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FEAT = "/home/ubuntu/closure-data/features"
DST = os.path.join(HERE, "FS2_DEGENERACY_REPORT.md")
a = json.load(open(os.path.join(FEAT, "fs2_audit.json")))
iv = json.load(open(os.path.join(FEAT, "invariance_check.json")))
man = json.load(open(os.path.join(FEAT, "manifest.json")))


def render(a, iv, man):
    """The whole document, rendered in memory. Returns (text, n_lines).

    Pure in its arguments: it reads nothing else and writes nothing. That is
    what lets the planted control below re-render the SAME code path from a
    perturbed audit dict instead of hand-writing a string that imitates it.
    """
    L = []
    A = L.append

    A("# FS2 degeneracy audit and FS5 extrapolation-coverage check")
    A("")
    A("**Generated** by `make_fs2_report.py` from `fs2_audit.json` and")
    A("`invariance_check.json`. Re-running reproduces it. **No model was trained.**")
    A("")
    A(f"Library: **{a['n_features']} features** on **{len(man['cases'])} cases**, "
      f"{sum(m['n_cells'] for m in man['cases'].values()):,} cells, zero non-finite values.")
    A(f"Numerical rank uses SVD of the column-standardised matrix with tolerance "
      f"`{a['rank_rcond']:g} * sigma_max`. A feature is DEAD if `max|v| < {a['zero_abs']:g}` "
      f"(absolute test only - see sec. 5).")
    A("")
    A("## 1. Feature-matrix rank per family")
    A("")
    A("| family | cells | rank | deficiency | dead | near-constant | `sigma_1/sigma_N` |")
    A("|---|---|---|---|---|---|---|")
    for f in a["families"] + ["POOLED"]:
        d = a["per_family"][f]
        A(f"| `{f}` | {d['n_cells']:,} | **{d['rank']}** / {d['n_features']} | {d['rank_deficiency']} | "
          f"{d['n_dead']} | {d['n_near_constant']} | {d['singular_value_ratio_first_to_last']:.2e} |")
    A("")
    A(f"**No family reaches full rank.** The ducts are worst: rank "
      f"**{a['per_family']['duct']['rank']} of {a['n_features']}** with "
      f"**{a['per_family']['duct']['n_dead']} algebraically-zero features**, and a condition number of "
      f"**{a['per_family']['duct']['singular_value_ratio_first_to_last']:.1e}**. Any method that "
      f"inverts or regularises this matrix on duct data is working in a space "
      f"{a['n_features'] - a['per_family']['duct']['rank']} dimensions smaller than it thinks.")
    A("")
    A("## 2. Features that are algebraically zero on ALL data (pooled)")
    A("")
    dead = a["per_family"]["POOLED"]["dead_features"]
    A(f"**{len(dead)} of {a['n_features']}**, listed in full:")
    A("")
    for n in dead:
        A(f"* `{n}`  (pooled `max|v|` = {a['per_feature'][n]['max']:.3e})")
    A("")
    A("Every one is a high-order invariant containing a product of three or more of "
      "`S`, `Omega`, `A_p`, `A_k`. They vanish because every case in this benchmark is a "
      "statistically two-dimensional mean flow - the same collapse that takes Pope's "
      "ten-tensor basis to rank 3 (sec. 4).")
    A("")
    A("### Dead per family (a feature can be dead on one family and live on another)")
    A("")
    A("| family | dead count |")
    A("|---|---|")
    for f in a["families"]:
        A(f"| `{f}` | {a['per_family'][f]['n_dead']} |")
    A("")
    A("## 3. Invariance check (charter section 6)")
    A("")
    A(f"Case `{iv['case']}`, {iv['n_cells']:,} cells. A Galilean boost "
      f"`c = {np.round(iv['tests']['galilean_boost']['c'],4).tolist()}` and a rigid rotation of "
      f"{iv['tests']['rotation']['angle_rad']} rad applied to the raw fields; every feature and "
      f"every normaliser recomputed. Tolerance `{iv['tolerance']:g}`.")
    A("")
    A(f"* **Rotation: max relative change {iv['tests']['rotation']['max_rel_change']:.3e}.** "
      f"{len(iv['not_rotation_invariant'])} features exceed tolerance and all three are artefacts, "
      "not failures: `trW2SWS2__A/B` are algebraically zero (`max|v|` ~ 3e-18, sec. 2) so the "
      "relative measure divides roundoff by zero, and `q8_kConvection` sits at 3.3e-12 for an "
      "O(1) feature. **All 110 features are rotation invariant to roundoff.**")
    A(f"* **Galilean boost: max relative change {iv['tests']['galilean_boost']['max_rel_change']:.3e}. "
      f"{len(iv['not_galilean_invariant'])} of {a['n_features']} features are NOT Galilean invariant.**")
    A("")
    ng = iv["not_galilean_invariant"]
    qs = [n for n in ng if n.startswith("q")]
    trs = [n for n in ng if n.startswith("tr") or n.startswith("I")]
    A(f"They fall into exactly two groups, and the split is the finding:")
    A("")
    A(f"**(a) {len(trs)} tensor invariants, every one of which contains `A_p`** - the "
      "antisymmetric tensor built from the pressure gradient. Wu, Xiao & Paterson normalise "
      "`grad p` by `rho |DU/Dt|` (their Table 1, preprint p. 8) and argue in Appendix C that the "
      "set is Galilean invariant. That argument holds for the **unsteady** material derivative "
      "`DU/Dt = dU/dt + U.grad U`, where the unsteady term supplies the compensating shift. "
      "**A steady RANS field has no `dU/dt`**, so the implementable normaliser is `|U.grad U|`, "
      "which is not boost-invariant - and neither is any invariant built on it. This is a property "
      "of steady-state implementation, not an error in the paper.")
    A("")
    A(f"**(b) {len(qs)} scalar features that use the raw velocity `U`:** "
      + ", ".join(f"`{n}`" for n in qs) + ".")
    A("")
    A("Full per-feature numbers are in `invariance_check.json`.")
    A("")
    A("## 4. Tensor-basis per-cell rank (charter section 5(b))")
    A("")
    t = a.get("tensor_basis_rank")
    if t:
        A(f"{t['method']}.")
        A("")
        A(f"* **Case means run {t['min_case_mean']:.3f} to {t['max_case_mean']:.3f}**; "
          f"mean of case means **{t['pooled_mean_of_case_means']:.3f}**.")
        A(f"* **Maximum rank reached in any cell of any case: {t['max_rank_any_cell']}.**")
        A("")
        A("**Provenance.** The charter (section 5(b)) records that a figure of \"3.24 on average, "
          "never above 5\" is quoted in three records from a pointer that does not resolve, and "
          "rules that it must not be quoted until it has a live source. **This table is that "
          "source.** It is a fresh measurement from `/home/ubuntu/closure-data/tbnn/dataset.npz` "
          "and it does not reproduce 3.24 as a *case-mean* statistic: the case means average "
          f"**{t['pooled_mean_of_case_means']:.3f}**. 3.24 was a *pooled-sample* number over "
          "randomly drawn training cells, which the duct cases - the lowest-rank family, at "
          f"{t['per_case']['AR_1_Ret_360']['mean_rank']:.3f} - pull down. Both are computable; they "
          "are different statistics and should not be quoted interchangeably. The bound that "
          f"matters is unchanged and is confirmed here: **never above {t['max_rank_any_cell']}, "
          "against a nominal basis size of 10.**")
        A("")
        A("| case | mean per-cell rank | min | max |")
        A("|---|---|---|---|")
        for c in sorted(t["per_case"], key=lambda x: t["per_case"][x]["mean_rank"]):
            v = t["per_case"][c]
            A(f"| `{c}` | {v['mean_rank']:.3f} | {v['min_rank']} | {v['max_rank']} |")
    A("")
    A("## 5. A criterion that had to be corrected, recorded")
    A("")
    A("The first version of this audit flagged a feature DEAD if `max|v|` fell below either an "
      "absolute threshold **or** `1e-12` times the largest value *anywhere in the matrix*. That "
      "relative test is meaningless on an incommensurable library: the Pope invariants under the "
      "Durbin-bounded normalisation reach `|lam3| = 1.5e11` and `|lam5| = 1.5e14`, so the relative "
      "threshold became **150** and every bounded feature - all eleven `q` markers, every "
      "normalised invariant - was reported dead. The test is now **absolute only**. Recorded "
      "because the wrong version produced a confident, plausible, entirely false answer.")
    A("")
    A("That the Pope invariants span fourteen orders of magnitude is itself an FS2 finding: they "
      "are the only unbounded block in the library, and they will dominate any unstandardised "
      "distance metric built on it.")
    A("")
    A("## 6. FS5 extrapolation coverage: TEST cases against the TRAINING range")
    A("")
    cv = a["coverage"]
    A(f"Training range is the per-feature min/max over the {len(cv['train_cases'])} non-TEST cases. "
      "A test cell is 'outside' if any feature falls beyond that range.")
    A("")
    A("| TEST case | cells | cells outside on >=1 feature | features ever outside |")
    A("|---|---|---|---|")
    for c, d in sorted(cv["per_test_case"].items(), key=lambda kv: kv[1]["frac_cells_any_feature_outside"]):
        A(f"| `{c}` | {d['n_cells']:,} | **{d['frac_cells_any_feature_outside']*100:.2f}%** | "
          f"{d['features_with_any_outside']} / {a['n_features']} |")
    A("")
    hump = cv["per_test_case"]["NASA_2DWMH"]
    A(f"**`NASA_2DWMH` is out of family by this instrument too**: "
      f"**{hump['frac_cells_any_feature_outside']*100:.2f}%** of its cells fall outside the training "
      f"range on at least one feature, and **{hump['features_with_any_outside']} of "
      f"{a['n_features']}** features go out of range somewhere on it. The four hills sit at "
      "0.00-0.06% and the three ducts at 0.96-3.07%. This is a third independent instrument "
      "agreeing with the Mahalanobis statistic (13.17% of hump cells beyond the training p99) and "
      "with the measured hump blow-up of every tensor-basis model.")
    A("")
    A("### Worst features on the hump, by fraction of cells out of range")
    A("")
    A("| feature | cells outside | worst excursion (training spans) |")
    A("|---|---|---|")
    for n, fr, be in hump["worst_features"]:
        A(f"| `{n}` | {fr*100:.2f}% | {be:.2f} |")
    A("")
    A("## 7. What this audit cannot see")
    A("")
    A("* **It is a degeneracy and coverage audit, not a selection.** Nothing is ranked by "
      "usefulness and nothing is removed. FS3 does that.")
    A("* **Rank is measured on the standardised matrix**, so it answers \"how many independent "
      "directions\" and not \"how well conditioned for a particular regressor\".")
    A("* **The invariance check ran on one case** (`CBFS13700`). The conclusions are algebraic and "
      "should hold everywhere, but they are measured on one field.")
    A("* **Dead-on-this-benchmark is not dead in general.** The twelve pooled-dead invariants vanish "
      "because these flows are two-dimensional; a three-dimensional case would revive them, and "
      "that is precisely why a model fitted here cannot be trusted there.")
    A("")
    return "\n".join(L) + "\n", len(L)


body, _n_lines = render(a, iv, man)

# ========================================================== REFUSAL GUARDS
# Two guards stand between this generator and its destination. Both run AFTER
# the document is rendered in memory and BEFORE anything is written, and both
# REFUSE (exit 2) rather than degrade -- the comparator discipline of CLAUDE.md
# rule 4. Neither is an `assert`: an assert vanishes under `python -O`, and a
# refusal that can be switched off from the command line is not a refusal.

# ---- GUARD 1: docket D491 clause (iv), the scope limit --------------------
# "`singular_value_ratio_first_to_last` is NOT to be quoted as a number in any
# closure record until a registered instrument decision adopts verification's
# recommendation (a)" -- FS5_D476_CLIP_REPAIR_RESULTS.md sec. A2.1, docket D491.
# Section 1 of this report renders exactly that statistic (the per-family table
# column, and the duct value in prose), so a re-run writes the forbidden figure
# into a committed record with nobody choosing to breach anything. It refuses.
#
# The scan is over the VALUE, not the key name, and that is the load-bearing
# design decision. The rendered text never contains the string
# "singular_value_ratio_first_to_last" -- it renders under the column header
# `sigma_1/sigma_N` and in prose as "condition number" -- so a name search
# returns a clean zero from a reader that could not have seen a non-zero.
# Rule 3 governs sweeps as much as comparators; the planted control below
# refuses if the scanner is blind.
#
# TO RELEASE: a registered instrument decision adopting recommendation (a) sets
# this to that decision's docket id. Editing this line is a measurement-script
# change and needs the closure supervisor's own diff read (SUPERVISION sec. 3).
D491_RELEASE = None          # None == guard armed

_FMTS = (".1e", ".2e", ".3e", ".4e", "g", ".6g")


def _renderings(x):
    out = set()
    for f in _FMTS:
        try:
            out.add(format(float(x), f))
        except (TypeError, ValueError):
            pass
    return out


def _scan_forbidden(text, src):
    """[(what, line_no)] for every place `text` quotes the forbidden statistic.

    Targets come from `src` -- the audit dict `text` was rendered FROM -- so the
    scanner is always asked about the values that this render actually saw, and
    the planted control below can hand it a perturbed dict and the perturbed
    render together.

    The value itself is never returned and never printed: a refusal message that
    prints the forbidden figure defeats the refusal it is announcing.
    """
    targets = {}
    for fam, d in src["per_family"].items():
        v = d.get("singular_value_ratio_first_to_last")
        if v is not None:
            targets[fam] = _renderings(v)
    hits = []
    for i, ln in enumerate(text.splitlines(), 1):
        if "singular_value_ratio_first_to_last" in ln:
            hits.append(("the key name", i))
        for fam in sorted(targets):
            if any(r in ln for r in targets[fam]):
                hits.append((f"per_family[{fam}] ratio, rendered", i))
    return hits


# ---- RULE 3, PLANTED CONTROL ---------------------------------------------
# The plant enters through the REAL data path and is read back off the REAL
# output path. A sentinel is substituted for the statistic in the audit dict
# that render() consumes; render() -- not this control -- formats it, at every
# site the generator quotes it; and the scanner is then run over render()'s own
# output. Nothing here authors the text the scanner has to match.
#
# The criterion is format-free and site-count-free. Substituting the sentinel
# can change a rendered line ONLY where the statistic is quoted, so EVERY line
# that differs between the real render and the planted render must be flagged by
# the scanner. A rendering format the scanner cannot read then shows up as a
# differing line that is NOT flagged, and the control refuses.
#
# The superseded form of this control (fs2_report_d491_guard_PROPOSED.diff:85)
# built its plant as format(value, '.2e') and searched a tuple containing
# '.2e'. It could not fail while the writer and the reader shared a format
# string, and it never touched render(): if the table at render()'s
# `{...:.2e}` or the prose at `{...:.1e}` had been written in any format
# outside _FMTS, that control would still have passed and the scan of the real
# body would still have returned a clean zero. A control that cannot fail is
# not a control, and a false control is worse than none.
_PLANT = 9.87654321e+05   # far from every real ratio (all >= 1e17 as measured)


def _planted_control(real_body):
    """(ok, detail). False on anything the control cannot positively establish."""
    ap = copy.deepcopy(a)
    n_planted = 0
    for fam in ap["per_family"]:
        if ap["per_family"][fam].get("singular_value_ratio_first_to_last") is not None:
            ap["per_family"][fam]["singular_value_ratio_first_to_last"] = _PLANT
            n_planted += 1
    if not n_planted:
        return False, ("no per_family entry carries "
                       "`singular_value_ratio_first_to_last`, so nothing could be "
                       "planted and the scanner is untested")
    planted, _ = render(ap, iv, man)
    b, p = real_body.splitlines(), planted.splitlines()
    if len(b) != len(p):
        return False, (f"planting changed the line count ({len(b)} -> {len(p)}); "
                       "the control cannot attribute differing lines to the plant")
    moved = [i + 1 for i in range(len(b)) if b[i] != p[i]]
    if not moved:
        return False, (f"a sentinel planted into {n_planted} per_family entries "
                       "changed NO rendered line: either this generator no longer "
                       "quotes the statistic, or the plant never reached render()")
    flagged = {n for _, n in _scan_forbidden(planted, ap)}
    blind = [n for n in moved if n not in flagged]
    if blind:
        return False, ("the scanner is BLIND where this generator writes the "
                       "statistic: planted render line(s) "
                       + ", ".join(str(n) for n in blind) +
                       " carry the planted value and the scanner does not see them")
    return True, (f"{n_planted} entries planted, {len(moved)} rendering site(s) "
                  f"changed, all {len(moved)} seen by the scanner")


_ok, _detail = _planted_control(body)
if not _ok:
    sys.stderr.write(
        "REFUSING: the D491 scope-limit scanner failed its planted control, so a "
        "clean report from it would not be evidence (CLAUDE.md rule 3).\n"
        f"  {_detail}\n"
        "  Nothing written.\n")
    sys.exit(2)

if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
    sys.stdout.write(f"planted control PASSED: {_detail}. Nothing written.\n")
    sys.exit(0)

_hits = _scan_forbidden(body, a)
if _hits and D491_RELEASE is None:
    sys.stderr.write(
        "REFUSING: this render quotes `singular_value_ratio_first_to_last` as a "
        "number in a committed closure record. Docket D491 clause (iv) forbids "
        "that until a registered instrument decision adopts verification's "
        "recommendation (a).\n"
        f"  destination: {DST}\n"
        "  occurrences (the value is withheld here, deliberately):\n"
        + "".join(f"    line {n}: {w}\n" for w, n in _hits) +
        "  This is NOT repaired by deleting the figure or by printing it with a "
        "non-binding label: a printed figure labelled non-binding is worse than "
        "one never computed, and a silent suppression turns a scope limit into "
        "invisible behaviour. Either the instrument decision is taken and "
        "D491_RELEASE names it, or this generator does not write.\n")
    sys.exit(2)

# ---- GUARD 2: cross-team audit pass 6 sec. 31.3, this file's variant ------
# make_feature_library.py was repaired to refuse when its destination carries
# hand-written lines PAST the generated text. That repair does not transfer
# here, and the reason is the whole point: this destination's rule-6 correction
# of 2026-08-22 (`fd3aa735`) is a bracketed sentence inserted INSIDE a generated
# paragraph, so the file on disk has the SAME line count as the render and a
# line-count guard sees nothing at all. Any difference between destination and
# render is either content this generator cannot reproduce, or a measured value
# that has moved since the record was written. Both are disclosures. Neither is
# made by overwriting.
if os.path.exists(DST):
    prev = open(DST).read()
    if prev != body:
        pl, bl = prev.splitlines(), body.splitlines()
        first = next((i + 1 for i in range(min(len(pl), len(bl)))
                      if pl[i] != bl[i]), min(len(pl), len(bl)) + 1)
        sys.stderr.write(
            f"REFUSING: {DST} on disk differs from this render.\n"
            f"  on disk {len(pl)} lines, render {len(bl)} lines; first "
            f"difference at line {first}.\n"
            "  A difference is either (a) a hand-written rule-6 correction this "
            "generator cannot reproduce -- the 2026-08-22 provenance bracket is "
            "one, and it carries ZERO line delta -- or (b) a measured value that "
            "has moved since the record was written, which is a re-grade and not "
            "a regeneration. Overwriting loses (a) silently and publishes (b) "
            "without disclosure.\n"
            "  Land the intended change as a dated amendment, or re-run with "
            "--regenerate '<reason>' having read the difference first.\n")
        if not (len(sys.argv) > 2 and sys.argv[1] == "--regenerate"):
            sys.exit(2)
        sys.stderr.write(f"  --regenerate accepted, reason: {sys.argv[2]}\n")

open(DST, "w").write(body)
print(f"wrote FS2_DEGENERACY_REPORT.md ({_n_lines + 1} lines)")
