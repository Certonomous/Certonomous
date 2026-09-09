#!/usr/bin/env python3
"""PATH (A): re-space the A3 validated structured volume (volumeMesh.xyz, 9 blocks, wall-normal=k)
to y+<1 (s0=1.546e-6) by redistributing points ALONG each existing wall-normal column curve --
preserves grid-line direction (hence A3's 61deg non-orth) while making the first cell y+<1.
Merges blocks via global-unique points; writes connected polyMesh; checkMesh verifies."""
import sys,os,numpy as np
A3="/home/ubuntu/certonomous-runs/A3-onera-m6-transonic"
outdir=sys.argv[1]; s0=1.546335364348132e-06
nk_out=int(sys.argv[2]) if len(sys.argv)>2 else 65   # wall-normal points after re-spacing
toks=open(A3+"/volumeMesh.xyz").read().split(); it=iter(toks); nb=int(next(it))
dims=[(int(next(it)),int(next(it)),int(next(it))) for _ in range(nb)]
blocks=[]
for d in dims:
    n=d[0]*d[1]*d[2]; vals=[float(next(it)) for _ in range(3*n)]
    X=np.array(vals[:n]).reshape(d,order='F'); Y=np.array(vals[n:2*n]).reshape(d,order='F'); Z=np.array(vals[2*n:3*n]).reshape(d,order='F')
    blocks.append(np.stack([X,Y,Z],-1))   # (ni,nj,nk,3), k=wall-normal
def geom_t(total,m,s0):
    # geometric arclength nodes 0..m, first cell s0, sum=total
    lo,hi=1.0+1e-12,5.0
    rt=total/s0
    for _ in range(90):
        md=.5*(lo+hi); g=(md**m-1)/(md-1); lo,hi=(md,hi) if g<rt else (lo,md)
    r=.5*(lo+hi); return np.array([s0*(r**k-1)/(r-1) for k in range(m+1)]),r
# re-space each column, build global points
gid={}; gpts=[]
def getid(p):
    k=(round(p[0],8),round(p[1],8),round(p[2],8))
    if k not in gid: gid[k]=len(gpts); gpts.append(p)
    return gid[k]
block_ids=[]; rmax=0
for B in blocks:
    ni,nj,nk=B.shape[:3]
    ids=np.empty((ni,nj,nk_out),dtype=np.int64)
    for i in range(ni):
        for j in range(nj):
            col=B[i,j]                      # (nk,3) wall->farfield
            seg=np.linalg.norm(np.diff(col,axis=0),axis=1); s=np.concatenate([[0],np.cumsum(seg)])
            tot=s[-1]
            t,r=geom_t(tot,nk_out-1,s0); rmax=max(rmax,r)
            # interpolate column coords at arclengths t
            newcol=np.empty((nk_out,3))
            for a in range(3): newcol[:,a]=np.interp(t,s,col[:,a])
            for k in range(nk_out): ids[i,j,k]=getid(newcol[k])
    block_ids.append(ids)
gpts=np.array(gpts)
# hex cells
cells=[]
for ids in block_ids:
    ni,nj,nk=ids.shape
    for i in range(ni-1):
        for j in range(nj-1):
            for k in range(nk-1):
                cells.append([ids[i,j,k],ids[i+1,j,k],ids[i+1,j+1,k],ids[i,j+1,k],
                              ids[i,j,k+1],ids[i+1,j,k+1],ids[i+1,j+1,k+1],ids[i,j+1,k+1]])
cells=np.array(cells,dtype=np.int64)
HEXF=[(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(3,0,4,7)]
fd={};fl=[];fo=[];fn=[]
for ci in range(len(cells)):
    c=cells[ci]
    for hf in HEXF:
        nd=(int(c[hf[0]]),int(c[hf[1]]),int(c[hf[2]]),int(c[hf[3]])); kk=tuple(sorted(nd))
        if kk in fd: fn[fd[kk]]=ci
        else: fd[kk]=len(fl); fl.append(nd); fo.append(ci); fn.append(-1)
fl=np.array(fl);fo=np.array(fo);fn=np.array(fn);internal=fn>=0
sw=internal&(fo>fn); fo[sw],fn[sw]=fn[sw].copy(),fo[sw].copy()
usedv=np.unique(cells); remap=-np.ones(len(gpts),dtype=np.int64); remap[usedv]=np.arange(len(usedv)); VPc=gpts[usedv]; fl=remap[fl]
cc=VPc[remap[cells]].mean(1); P0,P1,P2,P3=(VPc[fl[:,q]] for q in range(4))
nr=np.cross(P2-P0,P3-P1); ctr=.25*(P0+P1+P2+P3)
tgt=np.where(internal[:,None],cc[np.where(internal,fn,fo)]-cc[fo],ctr-cc[fo])
flip=np.einsum('ij,ij->i',nr,tgt)<0; fl[flip]=fl[flip][:,::-1]
ii=np.nonzero(internal)[0][np.lexsort((fn[internal],fo[internal]))]
bd=np.nonzero(~internal)[0]; bd=bd[np.argsort(fo[bd],kind='stable')]
F=fl[np.concatenate([ii,bd])]; OW=fo[np.concatenate([ii,bd])]; NE=fn[ii]; nint=len(ii)
d_=os.path.join(outdir,"constant","polyMesh"); os.makedirs(d_,exist_ok=True)
h=lambda cls,o:"FoamFile{version 2.0;format ascii;class %s;object %s;}\n\n"%(cls,o)
open(d_+"/points","w").write(h("vectorField","points")+f"{len(VPc)}\n(\n"+"\n".join("(%.17g %.17g %.17g)"%tuple(p) for p in VPc)+"\n)\n")
open(d_+"/faces","w").write(h("faceList","faces")+f"{len(F)}\n(\n"+"\n".join("4(%d %d %d %d)"%tuple(q) for q in F)+"\n)\n")
open(d_+"/owner","w").write(h("labelList","owner")+f"{len(OW)}\n(\n"+"\n".join(map(str,OW.tolist()))+"\n)\n")
open(d_+"/neighbour","w").write(h("labelList","neighbour")+f"{nint}\n(\n"+"\n".join(map(str,NE.tolist()))+"\n)\n")
open(d_+"/boundary","w").write(h("polyBoundaryMesh","boundary")+f"1\n(\n walls{{type patch;nFaces {len(F)-nint};startFace {nint};}}\n)\n")
print(f"respaced A3: cells={len(cells)} pts={len(VPc)} nk_out={nk_out} growth_r_max={rmax:.3f} s0={s0:.3e}")
