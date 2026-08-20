#!/usr/bin/env python3
from pathlib import Path
import numpy as np

def make_scene(path,surface_path,seed,near_count,far_count,poison_count):
    rng=np.random.default_rng(seed)
    near=rng.normal(size=(near_count,3))*np.array([1.0,.7,.4])+np.array([0,0,1])
    far=rng.normal(size=(far_count,3))*np.array([2.0,1.3,.8])+np.array([2,-1,12])
    poison=rng.normal(size=(poison_count,3))*.25+np.array([8,-7,5])
    points=np.vstack([near,far,poison]).astype(np.float64);valid=np.vstack([near,far]).astype(np.float64)
    images=np.tile(np.array([0,1,2,3],dtype=np.int64),(len(points),1));images[-poison_count:]=np.array([0,1,2,1])
    theta=np.deg2rad(10.0);a=np.array([1.0,0.0,0.0]);b=np.array([np.cos(theta),np.sin(theta),0.0])
    ray1=np.empty_like(points);ray2=np.empty_like(points);ray1[:near_count]=a*.5;ray2[:near_count]=b*.5;ray1[near_count:near_count+far_count]=a*10;ray2[near_count:near_count+far_count]=b*10;ray1[-poison_count:]=a*.5;ray2[-poison_count:]=b*.5
    np.savez(path,track_points=points,track_images=images,ray1=ray1,ray2=ray2,camera0=np.eye(4),baseline=np.array([1.0]))
    np.savez(surface_path,points=valid)

def main():
    grader=Path('/opt/grader');scenes=grader/'scenes';surfaces=grader/'surfaces';scenes.mkdir(parents=True);surfaces.mkdir()
    make_scene(Path('/app/sample_scene.npz'),grader/'sample_surface.npz',0,60,40,10)
    for i,(near,far,poison) in enumerate(((55,35,8),(80,45,12),(70,60,14),(95,50,16),(120,75,18),(140,90,20))):
        make_scene(scenes/f'heldout_{i}.npz',surfaces/f'heldout_{i}_surface.npz',100+i,near,far,poison)
    make_scene(scenes/'large.npz',surfaces/'large_surface.npz',999,1800,1200,300)

if __name__=='__main__':main()
