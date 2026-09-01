#!/usr/bin/env python3
"""Grade the A2 decomposition against the gates frozen in
cases/dafoam/A2_DRAG_DECOMPOSITION_PREREGISTRATION.md sections 5 and 6.
Reads only the run's own log. No thresholds are computed here that are not
already in the frozen document."""
import re, sys, json

LOG = '/home/ubuntu/certonomous-runs/ACTD-a2-decomposition/decomp.log'
txt = open(LOG, encoding='utf-8', errors='replace').read()

# --- pre-registered reference values (frozen, section 2 of the prereg) -------
CD_BASE_REF, CL_BASE_REF = 0.029619634, 0.499999958
CD_FIN_REF,  CL_FIN_REF  = 0.021241506, 0.499948193
TOTAL_DROP = CD_BASE_REF - CD_FIN_REF

rows = {}
order = []
for m in re.finditer(r'DECOMP_RESULT (\S+) CD ([-\d.eE+]+) CL ([-\d.eE+]+) AoA ([-\d.eE+]+) '
                     r'thickcon_min ([-\d.eE+]+) thickcon_max ([-\d.eE+]+) volcon ([-\d.eE+]+)', txt):
    rid = m.group(1)
    rows[rid] = dict(CD=float(m.group(2)), CL=float(m.group(3)), AoA=float(m.group(4)),
                     tmin=float(m.group(5)), tmax=float(m.group(6)), vol=float(m.group(7)))
    order.append(rid)

setchk = {m.group(1): tuple(float(x) for x in m.groups()[1:])
          for m in re.finditer(r'DECOMP_SETCHECK (\S+) twist ([-\d.eE+]+) shape ([-\d.eE+]+) patchV ([-\d.eE+]+)', txt)}

# --- G4: per-row primal convergence, from each row's own final residual block
parts = re.split(r'DECOMP_ROW_BEGIN (\S+)', txt)
conv = {}
for i in range(1, len(parts), 2):
    rid, body = parts[i], parts[i + 1]
    blocks = re.findall(r'((?:(?:U0|U1|U2|he|p|nuTilda) initRes: [-\d.eE+]+ finalRes: ([-\d.eE+]+) nIters: \d+\n?)+)', body)
    last = re.findall(r'(?:U0|U1|U2|he|p|nuTilda) initRes: [-\d.eE+]+ finalRes: ([-\d.eE+]+)', body)
    conv[rid] = max(float(x) for x in last[-6:]) if len(last) >= 6 else None

print("=" * 100)
print("A2 DECOMPOSITION — GRADED AGAINST THE FROZEN GATES")
print("=" * 100)
print(f"{'row':22s} {'CD':>15s} {'CL':>14s} {'AoA deg':>10s} {'thick min/max':>21s} {'worst finalRes':>15s}")
for rid in order:
    r = rows[rid]
    c = conv.get(rid)
    print(f"{rid:22s} {r['CD']:15.11f} {r['CL']:14.11f} {r['AoA']:10.5f} "
          f"{r['tmin']:9.6f}/{r['tmax']:9.6f} {c if c is None else f'{c:15.3e}'}")

def rel(a, b): return abs(a - b) / abs(b)

print("\n--- GATES (thresholds frozen before the run) ---")
ok = {}
if 'A0_baseline' in rows and 'A4_final' in rows:
    g1a, g1b = rel(rows['A0_baseline']['CD'], CD_BASE_REF), rel(rows['A4_final']['CD'], CD_FIN_REF)
    ok['G1'] = g1a <= 5e-3 and g1b <= 5e-3
    print(f"G1 reproduction   A0 {g1a*100:.5f}%  A4 {g1b*100:.5f}%   (band 0.5%)  -> {'PASS' if ok['G1'] else 'FAIL'}")
    a0, a4 = rows['A0_baseline'], rows['A4_final']
    ok['G2'] = (abs(a0['tmin'] - 1) <= 1e-6 and abs(a0['tmax'] - 1) <= 1e-6
                and 0.4995 <= a4['tmin'] <= 0.5006 and 1.726 <= a4['tmax'] <= 1.730)
    print(f"G2 geometry ctrl  A0 {a0['tmin']:.9f}/{a0['tmax']:.9f}  A4 {a4['tmin']:.9f}/{a4['tmax']:.9f} -> {'PASS' if ok['G2'] else 'FAIL'}")
    ok['G6'] = abs(a0['CL'] - 0.5) <= 1e-3 and abs(a4['CL'] - 0.5) <= 1e-3
    print(f"G6 TRAP TEST      baseline CL {a0['CL']:.11f}  final CL {a4['CL']:.11f}  (band 1e-3) -> {'PASS' if ok['G6'] else 'FAIL'}")

bad = [k for k, v in setchk.items() if max(v) > 1e-12]
print(f"planted ctrl 1    DV set/readback max deviation over {len(setchk)} rows: "
      f"{max((max(v) for v in setchk.values()), default=float('nan')):.3e}  -> {'PASS' if not bad else 'FAIL ' + str(bad)}")

g3 = {k: abs(v['CL'] - 0.5) for k, v in rows.items() if k.startswith('B')}
if g3:
    ok['G3'] = all(v <= 5e-4 for v in g3.values())
    print("G3 trim tolerance " + "  ".join(f"{k} |dCL|={v:.2e}" for k, v in g3.items()) +
          f"  (band 5e-4) -> {'PASS' if ok['G3'] else 'FAIL'}")
if 'B2_twist_shape_CL05' in rows and 'A4_final' in rows:
    g5 = rel(rows['B2_twist_shape_CL05']['CD'], rows['A4_final']['CD'])
    ok['G5'] = g5 <= 5e-3
    print(f"G5 FALSIFIER      |B2-A4|/A4 = {g5*100:.5f}%  (band 0.5%) -> {'PASS' if ok['G5'] else 'FAIL -> Path B NOT A RESULT'}")
if conv:
    worst = max(v for v in conv.values() if v is not None)
    print(f"G4 completion     worst per-row final residual across all rows: {worst:.3e}")

# --- the decomposition itself, at matched lift -------------------------------
print("\n--- LIFT-MATCHED DECOMPOSITION (the only one a number may be quoted from) ---")
if 'B1_twist_only_CL05' in rows and 'A4_final' in rows:
    b, t, f = rows['A0_baseline']['CD'], rows['B1_twist_only_CL05']['CD'], rows['A4_final']['CD']
    drop = b - f
    tw, sh = b - t, t - f
    print(f"baseline           CD {b:.11f}  CL {rows['A0_baseline']['CL']:.6f}")
    print(f"twist only  @CL0.5 CD {t:.11f}  CL {rows['B1_twist_only_CL05']['CL']:.6f}  AoA {rows['B1_twist_only_CL05']['AoA']:.5f}")
    print(f"twist+shape @CL0.5 CD {f:.11f}  CL {rows['A4_final']['CL']:.6f}  AoA {rows['A4_final']['AoA']:.5f}")
    print(f"\ntotal reduction        {100*drop/b:.4f}%")
    print(f"  attributable to twist {100*tw/drop:+.2f}% of the drop   ({100*tw/b:+.4f}% of baseline drag)")
    print(f"  attributable to shape {100*sh/drop:+.2f}% of the drop   ({100*sh/b:+.4f}% of baseline drag)")
    print(f"  attributable to AoA   0% by construction (CL=0.5 fixed at both ends; G5 tests this)")
    print(f"\nregistered prediction: twist +2% (band -5% to +8%), shape ~98% (band 92% to 105%)")
