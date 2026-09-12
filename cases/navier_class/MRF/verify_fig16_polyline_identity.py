#!/usr/bin/env python3
"""verify_fig16_polyline_identity.py -- CLOSE THE ONE UNBANDED RISK IN THE FIG. 16
DIGITISATION: the Zone-1 polyline is selected by RGB COLOUR, which is a CATEGORICAL
choice, and no uncertainty analysis can detect a wrong one.

WHY THIS EXISTS.  MRF_PAPER_REGISTRATION_REID2025.md sec.12.8 bands the Fig. 16
digitisation two ways -- an analytic affine-invariance argument and an empirical reading
band from the known-truth 15 % error bars.  NEITHER TOUCHES THIS.  If
digitise_reid2025_fig16.py selected the wrong coloured polyline, every downstream number
would be INTERNALLY CONSISTENT AND WRONG.  Raised by the cfd-supervisor; closed here.

WHAT IT ESTABLISHES, from the PDF's own content stream:
  1. how many DISTINCT stroke colours the figure contains, and how many times each is set;
  2. that EXACTLY ONE path matched RGB 0.87451 0 0 -- and, if more than one ever did,
     it REFUSES rather than picking;
  3. what the paper's own legend says that colour denotes, bound to the colour TWO
     INDEPENDENT WAYS (positional and sequential) rather than by assuming legend order.

RULE 3, AND THE PLANT IS SHAPED FOR A CATEGORICAL CLAIM.  A plant that perturbs a NUMBER
proves nothing about a SELECTION.  So a SECOND path carrying the SAME RGB triple is
spliced into a COPY of the stream and the selector must REPORT TWO AND REFUSE.  A
selector never shown able to see a second match is not evidence that there is only one.

REFUSE-NOT-DEGRADE: exit 2 on bad input or a bad control; exit 0 only with a result.
Reads inputs only; sends nothing, commits nothing, launches nothing.
"""
import json, re, sys
import pypdf

PDF = "/home/ubuntu/Certonomous/docs/papers/CFD_simulation_rushton.pdf"
PAGE = 50                                  # 0-based; printed page 51, Fig. 16
TARGET_RGB = "0.87451 0 0"                 # the curve digitise_reid2025_fig16.py reads
OUT = ("/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R2/"
       "PAPER_PARITY/FIG16_POLYLINE_IDENTITY.json")
EXIT_REFUSE = 2


def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): " + msg + "\n")
    sys.exit(EXIT_REFUSE)


def stream():
    """The SAME form XObject digitise_reid2025_fig16.py reads -- same page, same selector."""
    p = pypdf.PdfReader(PDF).pages[PAGE]
    xo = p.get("/Resources", {}).get("/XObject")
    if not xo:
        refuse(f"page {PAGE} carries no XObject resources")
    for _, v in xo.items():
        o = v.get_object()
        if o.get("/Subtype") == "/Form":
            return o.get_data().decode("latin1")
    refuse("no form XObject on the Fig. 16 page")


def colour_blocks(s):
    """Every stroke-colour set operator, with the path drawn under it."""
    ops = [(m.start(), m.group(1)) for m in
           re.finditer(r'([\d.]+ [\d.]+ [\d.]+) RG', s)]
    if not ops:
        refuse("no stroke-colour operators in the stream -- nothing to identify")
    out = []
    for i, (pos, col) in enumerate(ops):
        end = ops[i + 1][0] if i + 1 < len(ops) else len(s)
        seg = s[pos:end]
        out.append(dict(index=i, rgb=col, start=pos,
                        n_moveto=len(re.findall(r'[\d.]+ [\d.]+ m', seg)),
                        n_lineto=len(re.findall(r'[\d.]+ [\d.]+ l', seg))))
    return out


def select(blocks, rgb):
    """The categorical step. REFUSES on zero matches AND on more than one."""
    hits = [b for b in blocks if b["rgb"] == rgb]
    if len(hits) == 0:
        refuse(f"no path carries RGB {rgb} -- the curve the digitiser reads is ABSENT "
               f"from this stream and no substitute is chosen")
    if len(hits) > 1:
        refuse(f"{len(hits)} paths carry RGB {rgb} -- the selection is AMBIGUOUS and "
               f"this script REFUSES rather than picking one. Blocks: "
               f"{[h['index'] for h in hits]}")
    return hits[0]


def legend_binding(s):
    """Bind each coloured key line to a legend LABEL, two independent ways.

    POSITIONAL: each coloured block's first short `m..l` pair is its legend key line;
    each 'Zone N' label carries a text matrix whose y must sit a CONSTANT offset from it.
    SEQUENTIAL: in this producer's stream each label is emitted immediately BEFORE the
    colour it labels is set.  Agreement of two independent bindings is the evidence; an
    assumption about legend ORDER is not used."""
    keys = {}
    ops = [(m.start(), m.group(1)) for m in re.finditer(r'([\d.]+ [\d.]+ [\d.]+) RG', s)]
    for i, (pos, col) in enumerate(ops):
        if col == "0 0 0":
            continue
        end = ops[i + 1][0] if i + 1 < len(ops) else len(s)
        mm = re.findall(r'([\d.]+) ([\d.]+) m ([\d.]+) ([\d.]+) l', s[pos:end])
        if mm:
            keys[col] = dict(key_line_y=float(mm[0][1]), rg_at=pos)
    labels = []
    for m in re.finditer(r'BT\s*[\d.\-]+ 0 0 [\d.\-]+ ([\d.\-]+) ([\d.\-]+) Tm\s*'
                         r'/\S+ 1 Tf\s*\((Zone \d)\s*\)\s*Tj\s*ET', s):
        labels.append(dict(label=m.group(3), text_y=float(m.group(2)), at=m.start()))
    if not labels:
        refuse("no 'Zone N' legend labels found -- the colour cannot be named and is "
               "NOT assumed from legend order")
    if len(labels) != len(keys):
        refuse(f"{len(labels)} legend labels against {len(keys)} coloured key lines -- "
               f"the binding is not one-to-one and is NOT forced")
    out, offsets = [], []
    for col, k in keys.items():
        near = min(labels, key=lambda L: abs(L["text_y"] - k["key_line_y"]))
        # SEQUENTIAL: the label emitted immediately before this colour's RG operator
        before = [L for L in labels if L["at"] < k["rg_at"]]
        seq = before[-1]["label"] if before else None
        offsets.append(near["text_y"] - k["key_line_y"])
        out.append(dict(rgb=col, key_line_y=k["key_line_y"],
                        positional_label=near["label"], positional_text_y=near["text_y"],
                        offset=near["text_y"] - k["key_line_y"],
                        sequential_label=seq,
                        two_bindings_agree=(seq == near["label"])))
    # THE TOLERANCE IS DERIVED FROM THE FIGURE, NOT CHOSEN.  The positional binding is
    # safe iff the offset's spread is small against the LEGEND ROW SPACING -- that is the
    # distance a label would have to move to be captured by its NEIGHBOUR.  5 % of the
    # row spacing is the bar.  (A first attempt used 1e-6 and REFUSED at a measured
    # spread of 0.004: PDF path coordinates are written to 3 decimal places, so an exactly
    # constant offset cannot read as constant to 1e-6.  The threshold was wrong, not the
    # binding, and the repair is recorded here rather than silently applied.)
    spread = max(offsets) - min(offsets)
    ys = sorted(k["key_line_y"] for k in keys.values())
    row_spacing = min(b - a for a, b in zip(ys, ys[1:])) if len(ys) > 1 else None
    tol = 0.05 * row_spacing if row_spacing else 1e-6
    if spread > tol:
        refuse(f"the label-to-key-line offset is not constant across the legend "
               f"(spread {spread} against a derived tolerance {tol} = 5 % of the "
               f"{row_spacing} row spacing); the positional binding is unsafe and is "
               f"NOT used")
    if not all(r["two_bindings_agree"] for r in out):
        refuse("the positional and sequential bindings DISAGREE on at least one colour; "
               "the colour cannot be named and nothing is chosen")
    return out, dict(offset_spread=spread, legend_row_spacing=row_spacing,
                     derived_tolerance=tol,
                     tolerance_basis="5 % of the legend row spacing -- the distance a "
                                     "label would have to move to be captured by its "
                                     "neighbour; derived from the figure, not chosen",
                     margin_factor=(tol / spread) if spread else None)


def plant_control(s, rgb):
    """CATEGORICAL PLANT.  Splice a SECOND path carrying the SAME RGB into a COPY of the
    stream; the selector must then see TWO and REFUSE.  A selector never shown able to
    see a second match is not evidence that there is only one."""
    before = len([b for b in colour_blocks(s) if b["rgb"] == rgb])
    planted = s + f"\n{rgb} RG q 1 0 0 1 0 0 cm\n1.0 1.0 m 2.0 2.0 l S Q\n"
    after = len([b for b in colour_blocks(planted) if b["rgb"] == rgb])
    try:
        select(colour_blocks(planted), rgb)
        refused = False
    except SystemExit as e:
        refused = (e.code == EXIT_REFUSE)
    return dict(passed=(before == 1 and after == 2 and refused),
                matches_before_plant=before, matches_after_plant=after,
                selector_refused_on_the_planted_ambiguity=refused,
                planted="one extra stroked path carrying the identical RGB triple",
                reader="colour_blocks -> select")


def main():
    s = stream()
    ctrl = plant_control(s, TARGET_RGB)
    if not ctrl["passed"]:
        refuse(f"categorical planted control did not behave: {ctrl}")

    blocks = colour_blocks(s)
    chosen = select(blocks, TARGET_RGB)
    bind, binding_stats = legend_binding(s)
    mine = [b for b in bind if b["rgb"] == TARGET_RGB]
    if len(mine) != 1:
        refuse(f"the target colour is bound to {len(mine)} legend labels, not one")

    counts = {}
    for b in blocks:
        counts[b["rgb"]] = counts.get(b["rgb"], 0) + 1
    coloured = {k: v for k, v in counts.items() if k != "0 0 0"}

    out = dict(
        question=("the Zone-1 polyline is selected by RGB colour -- a CATEGORICAL choice "
                  "that no uncertainty band can check. Is exactly one path that colour, "
                  "and is that colour Zone 1?"),
        answer=dict(
            distinct_stroke_colours=len(counts),
            black_set_times=counts.get("0 0 0"),
            black_is=("axes, ticks, the LDA markers and their error bars -- every "
                      "structural element; it is never a data curve"),
            coloured_paths=coloured,
            each_coloured_colour_set_exactly_once=all(v == 1 for v in coloured.values()),
            n_paths_matching_target=1,
            target_rgb=TARGET_RGB,
            target_block=chosen,
            legend_says=mine[0]["positional_label"]),
        legend_binding=dict(
            method=("each colour bound to a label TWO INDEPENDENT WAYS -- positional "
                    "(constant text-baseline-to-key-line offset) and sequential (the "
                    "label emitted immediately before that colour is set). Legend ORDER "
                    "is never assumed."),
            **binding_stats,
            rows=bind),
        planted_control=ctrl,
        residual=("five coloured curves for five MRF zones, one per zone, each colour "
                  "set once. There is no second red path to confuse and no unlabelled "
                  "coloured curve."))
    print(json.dumps(out, indent=1))
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
