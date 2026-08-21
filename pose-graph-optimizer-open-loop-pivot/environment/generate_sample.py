#!/usr/bin/env python3
import importlib.util, math
from pathlib import Path
import numpy as np

def compose(a,b):
 c,s=math.cos(a[2]),math.sin(a[2]); return np.array([a[0]+c*b[0]-s*b[1],a[1]+s*b[0]+c*b[1],a[2]+b[2]])
def inverse(a):
 c,s=math.cos(a[2]),math.sin(a[2]); return np.array([-c*a[0]-s*a[1],s*a[0]-c*a[1],-a[2]])
def between(a,b): return compose(inverse(a),b)
def line_edge(edge_id,i,j,kind,z,cov): return 'EDGE %d %d %d %s %s %s\n'%(edge_id,i,j,kind,' '.join(f'{v:.10f}' for v in z),' '.join(f'{v:.10f}' for v in cov))

Path('/app/graphs').mkdir(); Path('/app/refs').mkdir(); rng=np.random.default_rng(0xfe275e45)
truth=[np.array([1.1*k,0.12*k*k,0.43*k]) for k in range(8)]; initial=[p+rng.normal(0,[0.08,0.08,0.03]) for p in truth]; initial[0]=truth[0].copy()
lines=[f'NODE {k} {p[0]:.10f} {p[1]:.10f} {p[2]:.10f}\n' for k,p in enumerate(initial)]; edge_id=1
diag=[0.015,0,0,0.015,0,0.008]
for k in range(7): lines.append(line_edge(edge_id,k,k+1,'ODOM',between(truth[k],truth[k+1]),diag)); edge_id+=1
for i,j in [(0,4),(2,7),(1,6)]:
 z=between(truth[j],truth[i]); z=z+np.array([0.015,-0.01,0.004]); lines.append(line_edge(edge_id,i,j,'LOOP',z,diag)); edge_id+=1
Path('/app/graphs/sample.pgraph').write_text(''.join(lines))
spec=importlib.util.spec_from_file_location('optimizer','/app/optimize.py'); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); module.INVERT_LOOPS=True; module.FULL_COVARIANCE=True; module.run('/app/graphs/sample.pgraph','/app/refs/sample.traj')

# Anisotropic fixture: diagonal weighting reaches a visibly different MLE.
truth=[np.array([0.9*k,0.18*k*k,0.36*k]) for k in range(9)]; initial=[p+rng.normal(0,[0.09,0.09,0.04]) for p in truth]; initial[0]=truth[0].copy()
lines=[f'NODE {k} {p[0]:.10f} {p[1]:.10f} {p[2]:.10f}\n' for k,p in enumerate(initial)]; edge_id=100
odom=[0.018,0.001,0.0005,0.016,0.0004,0.009]; loop_cov=[0.060,0.028,0.022,0.050,0.019,0.032]
for k in range(8): lines.append(line_edge(edge_id,k,k+1,'ODOM',between(truth[k],truth[k+1])+np.array([0.004,-0.003,0.001]),odom)); edge_id+=1
for n,(i,j) in enumerate([(0,5),(1,7),(3,8),(2,6)]):
 z=between(truth[j],truth[i])+np.array([0.11*(-1)**n,-0.075+0.015*n,0.045*(-1)**(n+1)]); lines.append(line_edge(edge_id,i,j,'LOOP',z,loop_cov)); edge_id+=1
Path('/app/graphs/aniso.pgraph').write_text(''.join(lines)); module.PIVOT_OUTPUT=False; module.WRITE_LOOP_REPORT=False; module.run('/app/graphs/aniso.pgraph','/app/refs/aniso.traj')

# Pivot fixture: path order is deliberately not numeric and rotations cross pi.
ids=[30,10,50,20,70,40,90]; truth=[np.array([0.7*k,0.11*k*k,1.12*k]) for k in range(len(ids))]; initial=[p+rng.normal(0,[0.06,0.06,0.025]) for p in truth]; initial[0]=truth[0].copy()
lines=[f'NODE {node_id} {p[0]:.10f} {p[1]:.10f} {p[2]:.10f}\n' for node_id,p in zip(ids,initial)]; edge_id=200
for k in range(len(ids)-1): lines.append(line_edge(edge_id,ids[k],ids[k+1],'ODOM',between(truth[k],truth[k+1]),odom)); edge_id+=1
loops=[]
for n,(a,b) in enumerate([(0,4),(1,6),(2,5)]):
 z=between(truth[b],truth[a])+np.array([0.04*(-1)**n,-0.03,0.018*(-1)**(n+1)]); lines.append(line_edge(edge_id,ids[a],ids[b],'LOOP',z,loop_cov)); loops.append(edge_id); edge_id+=1
Path('/app/graphs/pivot.pgraph').write_text(''.join(lines)); module.PIVOT_OUTPUT=True; module.run('/app/graphs/pivot.pgraph','/app/refs/pivot_continuous.traj')
Path('/app/refs/pivot_report.json').write_text(__import__('json').dumps([{'edge_id':value,'was_inverted':True} for value in loops],indent=2)+'\n')
