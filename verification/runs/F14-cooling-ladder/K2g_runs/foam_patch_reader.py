"""foam_patch_reader.py -- K2g.  The ONE reader every level is graded through.

Registered by `docs/campaigns/F14-cooling-ladder/K2g_PREREGISTRATION.md` section 4.
It computes an AREA-WEIGHTED patch average of a volScalarField from the field
files on disk, from EITHER a reconstructed time directory OR the decomposed
`processor*` directories, and section 9's C-RECON control asserts the two paths
agree on real data.  There is deliberately no second reader: K2f_L1 and K2f_L2
carry no p_rgh monitor, K2g_L3 would, and grading the coarse levels through one
instrument and the fine level through another is how a defect hides.
"""
import os, re, glob
import numpy as np

_COMMENT = re.compile(r'/\*.*?\*/', re.S)


def _strip(txt):
    return re.sub(r'//[^\n]*', ' ', _COMMENT.sub(' ', txt))


def _list_after(s, k, ncomp=1):
    """Parse the next OpenFOAM list at/after offset k.

    Two spellings occur and BOTH must be read: field files write
    ``List<scalar> N ( ... )`` and polyMesh files write a bare ``N ( ... )``.
    Reading only the first is how a mesh-side reader silently returns nothing.
    """
    m = re.compile(r'(?:List<\w+>\s*)?(\d+)\s*\(', re.S).search(s, k)
    if m is None:
        raise ValueError("no list found after offset %d" % k)
    start, depth, i = m.end(), 1, m.end()
    while depth:
        c = s[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        i += 1
    a = np.fromstring(s[start:i - 1].replace('(', ' ').replace(')', ' '), sep=' ')
    return a.reshape(-1, ncomp) if ncomp > 1 else a


def _after_header(path):
    """File text past the FoamFile block -- the count that follows is the list's."""
    raw = _strip(open(path).read())
    return raw[raw.index('}', raw.index('FoamFile')) + 1:]


def patch_values(field_path, patch, nfaces):
    """Face values of `patch` in `field_path`; `uniform` is expanded to nfaces."""
    body = _strip(open(field_path).read())
    bi = body.find('boundaryField')
    if bi < 0:
        raise ValueError("%s has no boundaryField" % field_path)
    m = re.compile(r'\n\s*' + re.escape(patch) + r'\s*\n?\s*\{').search(body, bi)
    if m is None:
        return None                      # patch absent (a processor without it)
    depth, j = 1, m.end()
    while depth:
        c = body[j]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        j += 1
    blk = body[m.end():j - 1]
    vk = blk.find('value')
    if vk < 0:
        raise ValueError("%s::%s has no `value` entry; it cannot be read"
                         % (field_path, patch))
    if 'nonuniform' in blk[vk:vk + 60]:
        return _list_after(blk, vk)
    mm = re.search(r'uniform\s+([-\d.eE+]+)\s*;', blk[vk:vk + 200])
    return np.full(nfaces, float(mm.group(1)))


def boundary_meta(polymesh):
    raw = _strip(open(os.path.join(polymesh, 'boundary')).read())
    out = {}
    for m in re.finditer(r'([A-Za-z_][\w.]*)\s*\{([^}]*)\}', raw):
        nf = re.search(r'nFaces\s+(\d+)', m.group(2))
        sf = re.search(r'startFace\s+(\d+)', m.group(2))
        if nf and sf:
            out[m.group(1)] = (int(nf.group(1)), int(sf.group(1)))
    return out


def _points(polymesh):
    return _list_after(_after_header(os.path.join(polymesh, 'points')), 0, ncomp=3)


def _patch_faces(polymesh, sf, nf):
    """Vertex lists of faces [sf, sf+nf).  The faces file holds ONE face per
    line, `4(a b c d)`, so the face index is the line index and only the patch's
    own slice is parsed -- a 2.0M-face L3 mesh is not walked to read 972 faces.
    """
    out, idx = [], -1
    with open(os.path.join(polymesh, 'faces')) as fh:
        started = False
        for ln in fh:
            t = ln.strip()
            if not started:
                if t == '(':
                    started = True
                continue
            if t == ')' or t == ')\n':
                break
            if not t or t.startswith('//'):
                continue
            idx += 1
            if idx < sf:
                continue
            if idx >= sf + nf:
                break
            k = t.index('(')
            out.append(np.fromstring(t[k + 1:t.rindex(')')], sep=' ',
                                     dtype=float).astype(np.int64))
    if len(out) != nf:
        raise ValueError("%s: read %d of %d faces from startFace %d"
                         % (polymesh, len(out), nf, sf))
    return out


def patch_face_areas(polymesh, patch):
    """|Sf| for every face of `patch`, by OpenFOAM's fan decomposition about the
    face centroid -- exact for planar polygons and correct for warped ones."""
    meta = boundary_meta(polymesh)
    if patch not in meta:
        return None
    nf, sf = meta[patch]
    pts = _points(polymesh)
    out = np.empty(nf)
    for i, f in enumerate(_patch_faces(polymesh, sf, nf)):
        v = pts[f]
        c = v.mean(axis=0)
        a = np.zeros(3)
        n = len(v)
        for e in range(n):
            a += np.cross(v[e] - c, v[(e + 1) % n] - c)
        out[i] = 0.5 * np.linalg.norm(a)
    return out


def area_average(case, time, field, patch):
    """Area-weighted average of `field` over `patch` at `time`.

    Reconstructed `<case>/<time>` when it exists, otherwise the union of
    `<case>/processor*/<time>`.  Both paths return the SAME number on a level
    that carries both, and section 9's C-RECON asserts it.
    """
    t = _tname(case, time)
    rec = os.path.join(case, t)
    if os.path.isdir(rec) and os.path.exists(os.path.join(rec, field)):
        pm = os.path.join(case, 'constant', 'polyMesh')
        nf = boundary_meta(pm).get(patch, (0, 0))[0]
        vals = patch_values(os.path.join(rec, field), patch, nf)
        ar = patch_face_areas(pm, patch)
        return float((vals * ar).sum() / ar.sum()), 'reconstructed'
    num = den = 0.0
    procs = sorted(glob.glob(os.path.join(case, 'processor*')))
    if not procs:
        raise ValueError("%s: neither %s/%s nor processor*/%s/%s exists"
                         % (case, t, field, t, field))
    for p in procs:
        pm = os.path.join(p, 'constant', 'polyMesh')
        meta = boundary_meta(pm)
        if patch not in meta:
            continue
        nf = meta[patch][0]
        vals = patch_values(os.path.join(p, t, field), patch, nf)
        ar = patch_face_areas(pm, patch)
        num += float((vals * ar).sum())
        den += float(ar.sum())
    if den == 0.0:
        raise ValueError("%s: patch %s carries no faces at %s" % (case, patch, t))
    return num / den, 'decomposed'


def internal_field(path, ncells):
    body = _strip(open(path).read())
    k = body.find('internalField')
    seg = body[k:k + 120]
    if 'nonuniform' not in seg:
        m = re.search(r'uniform\s+([-\d.eE+]+)\s*;', body[k:k + 300])
        return np.full(ncells, float(m.group(1)))
    return _list_after(body, k)


def _tname(case, time):
    """OpenFOAM's own spelling of the time directory (3000, not 3000.0)."""
    for cand in ("%g" % time, str(time), "%d" % int(time)):
        for root in (case, os.path.join(case, 'processor0')):
            if os.path.isdir(os.path.join(root, cand)):
                return cand
    return "%g" % time


def rms_departure(case, time, field, base_time=0):
    """RMS over internal cells of field(time) - field(base_time).

    This is the ALIVENESS half of the plateau test: a solve that never left its
    initial condition -- a frozen or dead solve -- returns ~0 here and MUST NOT
    be certified as plateaued merely because its late-checkpoint drift is small.
    """
    t, t0 = _tname(case, time), _tname(case, base_time)
    rec = os.path.join(case, t)
    if os.path.isdir(rec) and os.path.exists(os.path.join(rec, field)):
        a = internal_field(os.path.join(rec, field), 0)
        b = internal_field(os.path.join(case, t0, field), len(a))
        return float(np.sqrt(((a - b) ** 2).mean()))
    num = n = 0.0
    for p in sorted(glob.glob(os.path.join(case, 'processor*'))):
        a = internal_field(os.path.join(p, t, field), 0)
        b = internal_field(os.path.join(p, t0, field), len(a))
        num += float(((a - b) ** 2).sum())
        n += len(a)
    return float(np.sqrt(num / n))
