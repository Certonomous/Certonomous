#!/usr/bin/env python3
"""Geometric metrics of a tessellated PPTC CAD variant, for the CAD equivalence measurement.

Reports, in millimetres (the CAD's own units):
  triangle count, surface area, enclosed volume (divergence theorem), bounding box,
  radial surface-area distribution (to localise where two variants differ),
  blade count at r/R = 0.7, and the r/R = 0.7 section chord and max thickness.

Axis is x (established from the CAD bounding box); radius is sqrt(y^2 + z^2).
"""
import sys, struct
import numpy as np

R_PROP = 125.0  # mm, D/2


def read_stl(path):
    with open(path, 'rb') as f:
        head = f.read(5)
        f.seek(0)
        if head == b'solid':
            # could still be binary with a 'solid' header; decide on size
            data = f.read()
            try:
                txt = data.decode('ascii', errors='strict')
                if 'facet normal' in txt:
                    return read_ascii(txt)
            except UnicodeDecodeError:
                pass
            f.seek(0)
        return read_binary(f)


def read_ascii(txt):
    vals = []
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith('vertex '):
            vals.extend(float(x) for x in line.split()[1:4])
    a = np.asarray(vals, dtype=np.float64)
    return a.reshape(-1, 3, 3)


def read_binary(f):
    f.seek(80)
    n = struct.unpack('<I', f.read(4))[0]
    buf = np.frombuffer(f.read(n * 50), dtype=np.uint8)
    if buf.size != n * 50:
        raise SystemExit('truncated binary STL')
    buf = buf.reshape(n, 50)
    verts = buf[:, 12:48].copy().view(np.float32).astype(np.float64)
    return verts.reshape(n, 3, 3)


def metrics(tris, label):
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    cr = np.cross(v1 - v0, v2 - v0)
    area_t = 0.5 * np.linalg.norm(cr, axis=1)
    area = area_t.sum()
    vol = np.einsum('ij,ij->i', v0, np.cross(v1, v2)).sum() / 6.0
    pts = tris.reshape(-1, 3)
    bb = (pts.min(axis=0), pts.max(axis=0))
    cent = tris.mean(axis=1)
    r = np.hypot(cent[:, 1], cent[:, 2])
    print(f'--- {label}')
    print(f'  triangles           {len(tris)}')
    print(f'  surface area        {area:.3f} mm^2')
    print(f'  enclosed volume     {vol:.3f} mm^3   (sign {"+" if vol > 0 else "-"})')
    print(f'  bbox x   [{bb[0][0]:10.4f} {bb[1][0]:10.4f}]  len {bb[1][0]-bb[0][0]:9.4f}')
    print(f'  bbox y   [{bb[0][1]:10.4f} {bb[1][1]:10.4f}]  len {bb[1][1]-bb[0][1]:9.4f}')
    print(f'  bbox z   [{bb[0][2]:10.4f} {bb[1][2]:10.4f}]  len {bb[1][2]-bb[0][2]:9.4f}')
    print(f'  max radius          {np.hypot(pts[:,1], pts[:,2]).max():.4f} mm '
          f'(R_prop = {R_PROP}, D = {2*R_PROP/1000:.3f} m)')
    return dict(area=area, vol=vol, bb=bb, r=r, area_t=area_t, tris=tris)


def radial_profile(m, label, edges):
    r, at = m['r'], m['area_t']
    prof = np.zeros(len(edges) - 1)
    for i in range(len(edges) - 1):
        sel = (r >= edges[i]) & (r < edges[i + 1])
        prof[i] = at[sel].sum()
    return prof


def blade_section(tris, r_target, halfwidth=0.6):
    """Vertices in a thin cylindrical shell; cluster by angle into blades."""
    pts = tris.reshape(-1, 3)
    r = np.hypot(pts[:, 1], pts[:, 2])
    sel = np.abs(r - r_target) < halfwidth
    p = pts[sel]
    if len(p) < 50:
        return None
    th = np.arctan2(p[:, 2], p[:, 1])
    order = np.argsort(th)
    th_s, p_s = th[order], p[order]
    # split into angular clusters where the gap exceeds 10 degrees
    gaps = np.diff(th_s)
    brk = np.where(gaps > np.deg2rad(10))[0]
    groups = np.split(np.arange(len(th_s)), brk + 1)
    # merge wrap-around
    if len(groups) > 1 and (th_s[0] + 2 * np.pi - th_s[-1]) < np.deg2rad(10):
        groups[0] = np.concatenate([groups[0], groups[-1]])
        groups = groups[:-1]
    groups = [g for g in groups if len(g) >= 20]
    out = []
    for g in groups:
        q = p_s[g]
        # unroll onto the cylinder: (axial x, arc length r*theta unwrapped)
        tq = np.arctan2(q[:, 2], q[:, 1])
        tq = np.unwrap(np.sort(tq)) if False else tq
        t0 = np.median(tq)
        dt = (tq - t0 + np.pi) % (2 * np.pi) - np.pi
        u = r_target * dt          # circumferential coordinate
        w = q[:, 0]                # axial coordinate
        P = np.column_stack([u, w])
        # chord = maximum point-to-point distance in the section
        # (exact via all-pairs on the convex hull would be tidier; N is small)
        d2 = ((P[:, None, :] - P[None, :, :]) ** 2).sum(-1)
        i, j = np.unravel_index(np.argmax(d2), d2.shape)
        chord = np.sqrt(d2[i, j])
        e = P[j] - P[i]
        e = e / np.linalg.norm(e)
        nrm = np.array([-e[1], e[0]])
        off = (P - P[i]) @ nrm
        thick = off.max() - off.min()
        out.append((len(g), chord, thick, np.degrees(t0)))
    out.sort(key=lambda z: z[3])
    return out


if __name__ == '__main__':
    paths = sys.argv[1:]
    ms, labels = [], []
    for pth in paths:
        lab = pth.split('/')[-1]
        tris = read_stl(pth)
        ms.append(metrics(tris, lab))
        labels.append(lab)
        print()

    edges = np.array([0, 30, 35, 37.5, 40, 45, 50, 60, 70, 80, 87.5, 95, 105, 115, 125.1])
    print('=== radial surface-area distribution (mm^2 per shell), and the difference ===')
    profs = [radial_profile(m, l, edges) for m, l in zip(ms, labels)]
    hdr = f"{'r_lo':>6} {'r_hi':>6}" + ''.join(f' {l[:16]:>18}' for l in labels)
    if len(profs) == 2:
        hdr += f" {'diff':>12} {'diff%':>8}"
    print(hdr)
    for i in range(len(edges) - 1):
        row = f'{edges[i]:6.1f} {edges[i+1]:6.1f}' + ''.join(f' {p[i]:18.3f}' for p in profs)
        if len(profs) == 2:
            d = profs[1][i] - profs[0][i]
            base = profs[0][i] if profs[0][i] > 0 else float('nan')
            row += f' {d:12.3f} {100*d/base:8.2f}'
        print(row)
    print()

    for m, l in zip(ms, labels):
        print(f'=== blade section at r/R = 0.7 (r = {0.7*R_PROP:.2f} mm) : {l}')
        sec = blade_section(m['tris'], 0.7 * R_PROP)
        if sec is None:
            print('  too few points in the shell')
            continue
        print(f'  blades found: {len(sec)}')
        print(f"  {'#':>2} {'npts':>6} {'chord mm':>10} {'thick mm':>10} {'theta deg':>10}")
        for k, (n, c, t, a) in enumerate(sec):
            print(f'  {k:2d} {n:6d} {c:10.4f} {t:10.4f} {a:10.2f}')
        cs = np.array([s[1] for s in sec])
        ts = np.array([s[2] for s in sec])
        print(f'  chord mean {cs.mean():.4f}  sd {cs.std(ddof=1) if len(cs)>1 else 0:.4f}'
              f'   (Report 3752 c0.7 = 104.17 mm)')
        print(f'  thick mean {ts.mean():.4f}  sd {ts.std(ddof=1) if len(ts)>1 else 0:.4f}')
        print()
