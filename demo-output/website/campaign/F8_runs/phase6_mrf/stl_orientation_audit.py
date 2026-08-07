import struct, numpy as np
fn='/home/ubuntu/Certonomous/demo-output/website/campaign/F8_runs/phase6_mrf/constant/triSurface/blade.stl'
raw=open(fn,'rb').read()
if raw[:5]==b'solid' and b'facet' in raw[:200]:
    # ascii
    import re
    v=np.array(re.findall(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)', raw), dtype=float)
    tris=v.reshape(-1,3,3)
else:
    n=struct.unpack('<I', raw[80:84])[0]
    arr=np.frombuffer(raw[84:84+n*50], dtype=np.uint8).reshape(n,50)
    f=arr[:,:48].copy().view('<f4').reshape(n,12)
    tris=f[:,3:12].reshape(n,3,3).astype(float)
print('tris:', len(tris), 'bbox:', tris.reshape(-1,3).min(0).round(3), tris.reshape(-1,3).max(0).round(3))

def section(z0):
    z=tris[:,:,2]
    keep=(z.min(1)<z0)&(z.max(1)>z0)
    pts=[]
    for t in tris[keep]:
        for i in range(3):
            a,b=t[i],t[(i+1)%3]
            if (a[2]-z0)*(b[2]-z0)<0:
                s=(z0-a[2])/(b[2]-a[2]); p=a+s*(b-a); pts.append(p[:2])
    return np.array(pts)

R=5.029
def analyze(z0,tag):
    P=section(z0)
    if len(P)<10: print(tag,'no section'); return None
    # chord = farthest pair (use hull-ish: extremes)
    from itertools import combinations
    # subsample for speed
    idx=np.random.default_rng(0).choice(len(P), min(len(P),800), replace=False)
    Q=P[idx]
    d=np.linalg.norm(Q[:,None,:]-Q[None,:,:],axis=2)
    i,j=np.unravel_index(d.argmax(), d.shape)
    e1,e2=Q[i],Q[j]
    chord=np.linalg.norm(e1-e2)
    u=(e2-e1)/chord   # from e1 to e2
    v=np.array([-u[1],u[0]])
    # thickness profiles near each end to find LE (fat) vs TE (sharp)
    s=(P-e1)@u; h=(P-e1)@v
    def width(frac):
        m=(s>frac*chord-0.03*chord)&(s<frac*chord+0.03*chord)
        return h[m].max()-h[m].min() if m.sum()>1 else 0
    w1,w2=width(0.08), width(0.92)
    if w1>w2: LE,TE=e1,e2; sLE=0.0
    else: LE,TE=e2,e1; u=-u; v=np.array([-u[1],u[0]]); s=(P-LE)@u; h=(P-LE)@v
    # camber: mean offset of midline
    mids=[]
    for frac in np.linspace(0.15,0.85,15):
        m=(s>frac*chord-0.03*chord)&(s<frac*chord+0.03*chord)
        if m.sum()>1: mids.append(0.5*(h[m].max()+h[m].min()))
    camber=np.mean(mids)/chord
    # geometric angle: chord vector LE->TE angle w.r.t. rotor plane (y axis)
    cvec=TE-LE
    ang_from_y=np.degrees(np.arctan2(cvec[0], cvec[1]))  # angle of chord vs +y, x=downwind
    print(f"{tag} z={z0:+.3f} (r/R={abs(z0)/R:.2f}): chord={chord:.3f} m, LE=({LE[0]:+.3f},{LE[1]:+.3f}), TE=({TE[0]:+.3f},{TE[1]:+.3f}), "
          f"chord angle vs +y = {ang_from_y:+.1f} deg, camber(mid offset toward +v)={camber:+.4f}, widths LE~{max(w1,w2):.3f}/TE~{min(w1,w2):.3f}")
    return dict(z=z0,chord=chord,LE=LE,TE=TE,ang=ang_from_y,camber=camber)

res={}
for z0 in [0.30*R, 0.63*R, 0.95*R, -0.30*R, -0.63*R, -0.95*R]:
    res[z0]=analyze(z0, 'blade+' if z0>0 else 'blade-')
np.save('/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/stl_sections.npy', res, allow_pickle=True)
