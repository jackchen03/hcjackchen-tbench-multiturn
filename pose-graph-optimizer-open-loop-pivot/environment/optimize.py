#!/usr/bin/env python3
import json, math, sys
import numpy as np

INVERT_LOOPS = False
FULL_COVARIANCE = False
PIVOT_OUTPUT = False
WRITE_LOOP_REPORT = False

def wrap(a):
    value=(a+math.pi)%(2*math.pi)-math.pi
    return math.pi if value<=-math.pi+1e-12 else value

def compose(a,b):
    c,s=math.cos(a[2]),math.sin(a[2])
    return np.array([a[0]+c*b[0]-s*b[1],a[1]+s*b[0]+c*b[1],a[2]+b[2]],float)

def inverse(a):
    c,s=math.cos(a[2]),math.sin(a[2])
    return np.array([-c*a[0]-s*a[1],s*a[0]-c*a[1],-a[2]],float)

def between(a,b): return compose(inverse(a),b)

def parse(path):
    order=[]; nodes={}; edges=[]
    for raw in open(path):
        parts=raw.split()
        if not parts or parts[0].startswith('#'): continue
        if parts[0]=='NODE':
            node_id=int(parts[1]); order.append(node_id); nodes[node_id]=np.array(list(map(float,parts[2:5])))
        elif parts[0]=='EDGE':
            edges.append({'edge_id':int(parts[1]),'i':int(parts[2]),'j':int(parts[3]),'type':parts[4],'z':np.array(list(map(float,parts[5:8]))),'cov':np.array(list(map(float,parts[8:14])))})
    return order,nodes,edges

def covariance(values):
    c0,c1,c2,c3,c4,c5=values
    if FULL_COVARIANCE: return np.array([[c0,c1,c2],[c1,c3,c4],[c2,c4,c5]],float)
    return np.diag([c0,c3,c5])

def measurement(edge):
    return inverse(edge['z']) if edge['type']=='LOOP' and INVERT_LOOPS else edge['z']

def residual(xi,xj,z):
    err=between(z,between(xi,xj)); err[2]=wrap(err[2]); return err

def optimize(order,nodes,edges):
    anchor=order[0]; moving=[n for n in order if n!=anchor]; slots={n:k for k,n in enumerate(moving)}; poses={n:v.copy() for n,v in nodes.items()}; eps=1e-6
    for _ in range(35):
        h=np.zeros((3*len(moving),3*len(moving))); g=np.zeros(3*len(moving))
        for edge in edges:
            i,j=edge['i'],edge['j']; z=measurement(edge); r=residual(poses[i],poses[j],z); info=np.linalg.inv(covariance(edge['cov'])); jac={}
            for node in (i,j):
                if node==anchor: continue
                block=np.zeros((3,3))
                for axis in range(3):
                    changed=poses[node].copy(); changed[axis]+=eps
                    trial=residual(changed,poses[j],z) if node==i else residual(poses[i],changed,z)
                    delta=trial-r; delta[2]=wrap(delta[2]); block[:,axis]=delta/eps
                jac[node]=block
            for a,ja in jac.items():
                sa=slice(3*slots[a],3*slots[a]+3); g[sa]+=ja.T@info@r
                for b,jb in jac.items():
                    sb=slice(3*slots[b],3*slots[b]+3); h[sa,sb]+=ja.T@info@jb
        step=-np.linalg.solve(h+1e-8*np.eye(len(h)),g)
        for node in moving: poses[node]+=step[3*slots[node]:3*slots[node]+3]
        if np.linalg.norm(step)<1e-9: break
    return poses

def run(input_path,output_path):
    order,nodes,edges=parse(input_path); poses=optimize(order,nodes,edges)
    output_order=order if PIVOT_OUTPUT else sorted(order)
    angles=np.array([poses[node][2] for node in output_order])
    if PIVOT_OUTPUT: angles=np.unwrap(angles)
    else: angles=np.array([wrap(value) for value in angles])
    with open(output_path,'w') as out:
        for node,theta in zip(output_order,angles): out.write(f'{node} {poses[node][0]:.10f} {poses[node][1]:.10f} {theta:.10f}\n')
    if WRITE_LOOP_REPORT:
        report=[{'edge_id':edge['edge_id'],'was_inverted':bool(INVERT_LOOPS)} for edge in edges if edge['type']=='LOOP']
        with open('/app/loop_report.json','w') as out: json.dump(report,out,indent=2); out.write('\n')

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('usage: optimize.py <input> <output>')
    run(sys.argv[1],sys.argv[2])
