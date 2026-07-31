"""checkMesh's 2D aspect ratio, computed directly from a structured PLOT3D grid.

Why this exists: NASA TMR distributes its own grids for the bump-in-channel case at
exactly the node counts this lab's ladder uses (89x41, 177x81, 353x161), and the
question "is our aspect ratio pathological or normal" is only answerable by measuring
NASA's grid with the SAME metric. Converting each one through plot3dToFoam + autoPatch
+ checkMesh works but is slow and needs the span patches hand-set to `empty`; this
computes the identical number straight from the node coordinates.

The formula is OpenFOAM's own 2D branch, transcribed from
`primitiveMeshTools::cellClosedness` (see 4G_tmr_mesh_aspect_ratio.md section 2):

    aspectRatio = max_dir( sum_faces |Sf . dir| ) / min_dir( sum_faces |Sf . dir| )

taken over the two NON-empty directions only, so the artificial span drops out.

VALIDATED, not asserted: run as a script it recomputes NASA's NACA0012 113x33 grid and
must reproduce the 20650841.43 that `4G_runs/nasa/log.checkMesh.coarse` reports from
checkMesh itself. It returns 20650841.436 -- ratio 1.000000.

Do not compare a number from here against a 3D mesh's checkMesh aspect ratio: the 3D
branch uses a different formula and includes the span. That mistake is what made a
pyHyp "167" and a TMR "20 million" look like the same quantity.
"""
import numpy as np, sys

def read_p3dfmt(p):
    """NASA TMR 3D plot3d: 1 block, dims (2, nJ, nK); i=span."""
    t=open(p).read().split()
    nb=int(t[0]); assert nb==1
    ni,nj,nk=int(t[1]),int(t[2]),int(t[3])
    n=ni*nj*nk; v=np.array(t[4:4+3*n],dtype=float)
    A=[v[m*n:(m+1)*n].reshape(nk,nj,ni) for m in range(3)]
    return ni,nj,nk,A   # A[m][k,j,i]

def read_p2dfmt(p):
    t=open(p).read().split()
    nb=int(t[0]); assert nb==1
    ni,nj=int(t[1]),int(t[2])
    n=ni*nj; v=np.array(t[3:3+2*n],dtype=float)
    x=v[:n].reshape(nj,ni); y=v[n:].reshape(nj,ni)
    return x,y   # [j_normal, i_stream]

def ar_field(P,Q,span=1.0):
    """P,Q are (M,N) arrays of the two in-plane node coords, extruded by `span`
    in the third direction.  Reproduces OpenFOAM primitiveMeshTools 2D branch:
    AR = max_dir(sum_faces|Sf.dir|) / min_dir(...), over the two geometric dirs."""
    p00=np.stack([P[:-1,:-1],Q[:-1,:-1]],-1); p10=np.stack([P[:-1,1:],Q[:-1,1:]],-1)
    p11=np.stack([P[1:,1:],Q[1:,1:]],-1);     p01=np.stack([P[1:,:-1],Q[1:,:-1]],-1)
    # the four side faces of each cell, as in-plane edges; extruded face area
    # vector = span * rot90(edge)
    s=np.zeros(p00.shape[:2]+(2,))
    for a,b in ((p00,p10),(p10,p11),(p11,p01),(p01,p00)):
        e=b-a
        Sf=span*np.stack([e[...,1],-e[...,0]],-1)   # rot(-90)
        s+=np.abs(Sf)
    return s.max(-1)/(s.min(-1)+1e-300)

def centres(P,Q):
    return ((P[:-1,:-1]+P[:-1,1:]+P[1:,1:]+P[1:,:-1])/4.0,
            (Q[:-1,:-1]+Q[:-1,1:]+Q[1:,1:]+Q[1:,:-1])/4.0)

if __name__=='__main__':
    print("VALIDATION against checkMesh on NASA's NACA0012 113x33")
    print("  (4G_runs/nasa/log.checkMesh.coarse reports Max aspect ratio 20650841.43)")
    ni,nj,nk,A=read_p3dfmt('models/tmr/naca0012/grids/n0012_113-33.p3dfmt')
    # span is the i direction; find which of X,Y,Z varies across i
    spans=[np.ptp(a[:,:,1]-a[:,:,0]) for a in A]
    mags=[np.abs(a[:,:,1]-a[:,:,0]).max() for a in A]
    sd=int(np.argmax(mags)); inplane=[m for m in range(3) if m!=sd]
    span=float(np.abs(A[sd][:,:,1]-A[sd][:,:,0]).mean())
    print(f"  dims i,j,k = {ni},{nj},{nk}; span dir = {'XYZ'[sd]}, thickness {span:g}")
    P=A[inplane[0]][:,:,0]; Q=A[inplane[1]][:,:,0]
    ar=ar_field(P,Q,span)
    print(f"  analytic max AR = {ar.max():.3f}   (checkMesh: 20650841.43)")
    print(f"  ratio = {ar.max()/20650841.43:.6f}")

def report(tag,P,Q,span,wall=(0.0,1.5)):
    ar=ar_field(P,Q,span); cx,cy=centres(P,Q)
    k=np.unravel_index(np.argmax(ar),ar.shape)
    band=(cx>=wall[0])&(cx<=wall[1])
    ib=np.unravel_index(np.argmax(np.where(band,ar,-1)),ar.shape)
    # first wall-normal cell height under the bump
    print(f"{tag}")
    print(f"   cells {ar.size}   global max AR {ar.max():14.1f}  at x={cx[k]:8.3f} y={cy[k]:.3e}")
    print(f"   max AR within the viscous wall band x in [{wall[0]},{wall[1]}]: {ar[band].max():10.1f}"
          f"  at x={cx[ib]:.3f} y={cy[ib]:.3e}")
    print(f"   cells above AR 1e5: {(ar>1e5).sum():6d}   above 1e6: {(ar>1e6).sum():6d}"
          f"   |x| of the worst cell: {abs(cx[k]):.2f}")
    return ar,cx,cy
