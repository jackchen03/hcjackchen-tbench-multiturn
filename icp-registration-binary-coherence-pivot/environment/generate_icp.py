#!/usr/bin/env python3
import json
from pathlib import Path
import numpy as np

def rotation(axis,angle):
    axis=np.asarray(axis,dtype=float);axis/=np.linalg.norm(axis);x,y,z=axis;c=np.cos(angle);s=np.sin(angle);C=1-c
    return np.array([[c+x*x*C,x*y*C-z*s,x*z*C+y*s],[y*x*C+z*s,c+y*y*C,y*z*C-x*s],[z*x*C-y*s,z*y*C+x*s,c+z*z*C]])

def transform(axis,angle,translation):
    matrix=np.eye(4);matrix[:3,:3]=rotation(axis,angle);matrix[:3,3]=translation;return matrix

def apply(points,normals,matrix):
    return points@matrix[:3,:3].T+matrix[:3,3],normals@matrix[:3,:3].T

def write_ply(path,points,normals):
    with open(path,'w',encoding='ascii',newline='\n') as f:
        f.write('ply\nformat ascii 1.0\n');f.write(f'element vertex {len(points)}\n')
        for name in ('x','y','z','nx','ny','nz'):f.write(f'property float {name}\n')
        f.write('end_header\n')
        for p,n in zip(points,normals):f.write(' '.join(format(float(v),'.12g') for v in (*p,*n))+'\n')

def cloud(seed,n,center=(0,0,0),scale=(1.2,.7,.35)):
    rng=np.random.default_rng(seed);points=rng.normal(size=(n,3))*np.asarray(scale)+np.asarray(center)
    normals=rng.normal(size=(n,3));normals/=np.linalg.norm(normals,axis=1)[:,None]
    return points,normals

def make_pair(root,name,kind,seed,matrix,n_core=300):
    core,core_n=cloud(seed,n_core);target_core,target_n=apply(core,core_n,matrix)
    if kind=='clean':src,src_n,tgt,tgt_n=core,core_n,target_core,target_n
    elif kind=='partial':
        clutter,clutter_n=cloud(seed+500,120,center=(8,-7,5),scale=(2,2,2));src=np.vstack([core,clutter]);src_n=np.vstack([core_n,clutter_n]);tgt,tgt_n=target_core,target_n
    else:
        wrong,wrong_n=cloud(seed+700,180,center=(4,4,-3),scale=(.8,.6,.4));alternate=transform((-.4,.2,1),-.022,(-.018,.012,-.009));wrong_t,wrong_tn=apply(wrong,wrong_n,alternate)
        # Incompatible normals identify the fringe cluster for the gated extension.
        axes=np.tile(np.array([1.0,0.0,0.0]),(len(wrong_n),1));axes[np.abs(wrong_n[:,0])>.9]=np.array([0.0,1.0,0.0])
        wrong_tn=np.cross(wrong_n,axes);wrong_tn/=np.linalg.norm(wrong_tn,axis=1)[:,None]
        src=np.vstack([core[:220],wrong]);src_n=np.vstack([core_n[:220],wrong_n]);tgt=np.vstack([target_core[:220],wrong_t]);tgt_n=np.vstack([target_n[:220],wrong_tn])
    write_ply(root/f'{name}.src.ply',src,src_n);write_ply(root/f'{name}.tgt.ply',tgt,tgt_n);np.savetxt(root/f'{name}.txt',matrix,fmt='%.12g')

def main():
    app=Path('/app');samples=app/'samples';dense=app/'samples_dense';profile=app/'profile_trace';samples.mkdir();dense.mkdir();profile.mkdir()
    cases=[('clean_0','clean',10,transform((.3,.7,.2),.018,(.016,-.012,.008))),('clean_1','clean',11,transform((.5,-.1,.8),-.017,(-.012,.014,.01))),('partial_0','partial',20,transform((.2,.9,-.3),.021,(.014,.01,-.013))),('outlier_0','outlier',30,transform((.6,.2,.7),.02,(.015,-.011,.012)))]
    shipped_gold=Path('/opt/grader/shipped_golden');shipped_gold.mkdir(parents=True)
    for name,kind,seed,matrix in cases:
        make_pair(samples,name,kind,seed,matrix);(samples/f'{name}.txt').replace(shipped_gold/f'{name}.txt')
    dense_matrix=transform((.2,-.8,.5),.014,(.009,.013,-.008));make_pair(dense,'dense_0','clean',50,dense_matrix,n_core=6000);(dense/'dense_0.txt').replace(shipped_gold/'dense_0.txt')
    profile.joinpath('README.md').write_text('Exact all-pairs correspondence search dominates this 6000-point trace. Deployment budget: under 5 seconds.\n')
    pairs=Path('/opt/grader/pairs');gold=Path('/opt/grader/golden');pairs.mkdir();gold.mkdir()
    hidden=[]
    for i in range(3):hidden.append((f'clean_{i}','clean',100+i,transform((.2+i,.5,.7),.012+i*.002,(.006+i*.002,-.009,.007))))
    for i in range(4):hidden.append((f'partial_{i}','partial',200+i,transform((.4,.8-i*.1,.3),.015+i*.001,(.01,-.007+i*.001,.009))))
    for i in range(3):hidden.append((f'outlier_{i}','outlier',300+i,transform((.7,.2,.5+i*.1),.016+i*.001,(.011,-.008,.006+i*.002))))
    for name,kind,seed,matrix in hidden:
        make_pair(pairs,name,kind,seed,matrix);(pairs/f'{name}.txt').replace(gold/f'{name}.txt')
    make_pair(pairs,'dense_0','clean',450,transform((.3,.4,.8),.013,(.008,-.006,.011)),n_core=6000);(pairs/'dense_0.txt').replace(gold/'dense_0.txt')
    Path('/opt/grader/manifest.json').write_text(json.dumps({'seeded':True,'dense_points':6000})+'\n')

if __name__=='__main__':main()
