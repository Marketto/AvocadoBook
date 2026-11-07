import numpy as np, trimesh, sys
from PIL import Image
def view(meshes, el, az, S=520):
    el,az=np.radians(el),np.radians(az)
    f=np.array([np.cos(el)*np.sin(az), -np.cos(el)*np.cos(az), np.sin(el)])  # camera dir (from target to cam)
    r=np.cross([0,0,1],f); r/=np.linalg.norm(r); u=np.cross(f,r)
    allv=np.vstack([m.vertices for m,_ in meshes]); c=(allv.max(0)+allv.min(0))/2; rad=np.linalg.norm(allv.max(0)-allv.min(0))/2
    img=np.ones((S,S,3))*0.97; zb=np.full((S,S),-1e9)
    Ld=f*0.6+u*0.5+r*0.3; Ld/=np.linalg.norm(Ld)
    for m,col in meshes:
        v=m.vertices-c; P=np.stack([v@r, v@u, v@f],1); P[:,:2]=(P[:,:2]/rad*0.48+0.5)*S; P[:,1]=S-P[:,1]
        n=m.face_normals; sh=0.3+0.7*np.abs(n@Ld)**0.8; col=np.array(col)
        for fi,tri in enumerate(m.faces):
            p=P[tri]; x0,y0=np.floor(p[:,:2].min(0)).astype(int); x1,y1=np.ceil(p[:,:2].max(0)).astype(int)
            x0,y0=max(x0,0),max(y0,0); x1,y1=min(x1,S-1),min(y1,S-1)
            if x1<x0 or y1<y0: continue
            xs,ys=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
            (ax,ay,az_),(bx,by,bz),(cx,cy,cz)=p
            d=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
            if abs(d)<1e-12: continue
            w0=((by-cy)*(xs-cx)+(cx-bx)*(ys-cy))/d; w1=((cy-ay)*(xs-cx)+(ax-cx)*(ys-cy))/d; w2=1-w0-w1
            ins=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6)
            if not ins.any(): continue
            z=w0*az_+w1*bz+w2*cz
            sub=zb[y0:y1+1,x0:x1+1]; ok=ins&(z>sub)
            sub[ok]=z[ok]; img[y0:y1+1,x0:x1+1][ok]=col*sh[fi]
    return (np.clip(img,0,1)*255).astype(np.uint8)
def render(meshes,out,views):
    ims=[view(meshes,e,a) for e,a in views]
    row=lambda a: np.hstack(a)
    Image.fromarray(np.vstack([row(ims[:2]),row(ims[2:])])).save(out)
if __name__=='__main__':
    C=dict(zip(sys.argv[2].split(','),[]))
    pal=[np.array(eval(x)) for x in sys.argv[3].split(';')]
    names=['1_body','2_screen','3_keys','4_logo']
    ms=[(trimesh.load(f'{n}.stl'),pal[i]) for i,n in enumerate(names)]
    render(ms,sys.argv[1],[(25,-35),(20,155),(65,0),(8,-10)])
