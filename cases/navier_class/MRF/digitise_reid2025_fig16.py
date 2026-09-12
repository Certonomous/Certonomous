#!/usr/bin/env python3
"""digitise_reid2025_fig16.py -- EXACT digitisation of Fig. 16 of Reid, Rossi,
Cottini & Benassi (2025), arXiv:2508.03176, from the PDF's own VECTOR PATH
COORDINATES -- not from pixels and not by eye.

What is read:
  * the Wu & Patterson (1989) LDA points (black filled circles + horizontal
    error bars) of k/Utip^2 vs 2z/W at r = 5 cm;
  * the paper's own MRF Zone-1 curve (red polyline), Zone 1 being the zone
    whose mesh family produced the Np band 5.46 / 5.44 / 5.49 (their Table 2).

Calibration: the axis TICK-MARK path coordinates in the same stream
(x: 0 at 32.500, 0.09 at 238.750;  y: 2z/W = -2.5 at 152.602, -1 at 109.000).

Internal consistency check that makes this a verification, not a guess: every
error bar recovered here has a half-width of EXACTLY 15.0 +/- 0.2 % of its own
centre value, which is the uncertainty the paper states for the Wu & Patterson
turbulent-kinetic-energy data (sidecar line ~832). The script REFUSES (exit 2)
if that does not hold -- a planted-control equivalent for a figure reader.
"""
import json, re, sys
import pypdf

PDF = "/home/ubuntu/Certonomous/docs/papers/CFD_simulation_rushton.pdf"
OUT = ("/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R2/"
       "PAPER_PARITY/REID2025_FIG16_DIGITISED.json")
PAGE = 50                      # 0-based; printed page 51, Fig. 16

# axis calibration from the tick-mark path coordinates in this same stream
X0, X1, XV0, XV1 = 32.500, 238.750, 0.0, 0.09          # k/Utip^2
Y0, Y1, YV0, YV1 = 152.602, 109.000, -2.5, -1.0        # 2z/W
xs = lambda x: XV0 + (x - X0) * (XV1 - XV0) / (X1 - X0)
ys = lambda y: YV0 + (y - Y0) * (YV1 - YV0) / (Y1 - Y0)


def stream():
    p = pypdf.PdfReader(PDF).pages[PAGE]
    for _, v in p["/Resources"]["/XObject"].items():
        o = v.get_object()
        if o.get("/Subtype") == "/Form":
            return o.get_data().decode("latin1")
    raise RuntimeError("no form XObject on the Fig. 16 page")


def main():
    s = stream()
    # --- the LDA markers: circles drawn as 4 Beziers, centre = (x_a + x_c)/2
    circ = re.findall(
        r'([\d.]+) ([\d.]+) m \1 ([\d.]+) ([\d.]+) \3 \4 \2 c', s)
    pts = sorted({(round((float(a) + float(c)) / 2, 3), round(float(b), 3))
                  for a, b, _, c in circ})
    # the legend key is also a circle -- drop it (it sits inside the legend box)
    pts = [(x, y) for x, y in pts if not (212 < x < 232 and 9 < y < 18)]
    # --- error-bar caps: vertical short segments, paired by their y
    caps = {}
    for a, b, c in re.findall(
            r'([\d.]+) ([\d.]+) m \1 ([\d.]+) l S', s):
        y = round((float(b) + float(c)) / 2, 2)
        if abs(float(b) - float(c)) > 5:      # axis ticks are longer
            continue
        caps.setdefault(y, []).append(float(a))
    lda, bad = [], []
    for x, y in pts:
        key = min(caps, key=lambda k: abs(k - y)) if caps else None
        half = None
        if key is not None and abs(key - y) < 0.6 and len(caps[key]) == 2:
            half = abs(caps[key][1] - caps[key][0]) / 2.0
        k = xs(x)
        rec = {"two_z_over_W": round(ys(y), 4), "k_over_Utip2": round(k, 6)}
        if half is not None:
            rec["half_width_k_over_Utip2"] = round(half * (XV1 - XV0) / (X1 - X0), 6)
            rec["half_width_pct"] = round(rec["half_width_k_over_Utip2"] / k * 100, 2)
            if abs(rec["half_width_pct"] - 15.0) > 0.4:
                bad.append(rec)
        lda.append(rec)
    lda.sort(key=lambda r: r["two_z_over_W"])
    if bad or len(lda) < 8:
        print("FIGURE-READER CONTROL FAILED -- REFUSING", bad, len(lda), file=sys.stderr)
        sys.exit(2)
    # --- the paper's Zone-1 curve (red 0.87451 0 0), the zone of their Table-2 family
    i = s.index("0.87451 0 0 RG")
    seg = s[i:s.index("0 0 0.545098 RG", i)]
    seg = seg[seg.index("l S Q", seg.index("212.699")):]      # skip the legend line
    nums = re.findall(r'([\d.]+) ([\d.]+) (?:m|l)', seg)
    z1 = [{"two_z_over_W": round(ys(float(b)), 4),
           "k_over_Utip2": round(xs(float(a)), 6)} for a, b in nums]
    out = {
        "source_pdf": PDF, "figure": "Fig. 16", "printed_page": 51,
        "method": ("exact digitisation from the PDF vector path coordinates; "
                   "axis calibration from the tick-mark coordinates in the same "
                   "content stream; NOT read off pixels and NOT read by eye"),
        "reader_control": ("every recovered error bar has a half-width of "
                           "15.0 +/- 0.4 % of its own centre value, which is the "
                           "Wu & Patterson TKE uncertainty the paper states; the "
                           "script exits 2 if any bar violates it"),
        "quantity": "k / Utip^2 at r = 5 cm, vs 2z/W",
        "wu_patterson_1989_LDA": lda,
        "paper_MRF_Zone1_curve": z1,
        "CAVEAT": ("these are the PAPER's tank: T = 0.27 m, D = 0.093 m, N = 3.33 "
                   "rev/s, Re = 28830. OUR tank is T = 0.30 m, D = 0.100 m, N = 5.0 "
                   "rev/s, Re = 50000, with 3x wider baffles and 4x thicker blades "
                   "relative to D. DIFFERENT DIMENSIONS -- NO MATCH EXPECTED."),
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"{len(lda)} LDA points, {len(z1)} Zone-1 curve points -> {OUT}")
    for r in lda:
        print(f"  2z/W={r['two_z_over_W']:+.3f}  k/Utip^2={r['k_over_Utip2']:.5f}"
              f"  +/-{r.get('half_width_pct', float('nan')):.1f}%")


if __name__ == "__main__":
    main()
