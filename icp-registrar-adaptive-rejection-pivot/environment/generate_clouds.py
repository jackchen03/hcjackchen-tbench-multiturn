#!/usr/bin/env python3
from pathlib import Path
import numpy as np
rng=np.random.default_rng(85374)
Path('/app/test_gt').mkdir(parents=True,exist_ok=True)
for index,(nsrc,ntgt) in enumerate([(180,120),(150,95),(220,180),(130,80)]):
    src=rng.normal(0,1,size=(nsrc,3)); delta=np.array([0.12+0.01*index,-0.07+0.005*index,0.035-0.003*index]); core=src[:min(nsrc,ntgt)]+delta; tgt=np.vstack([core,rng.normal(3,1.4,size=(ntgt-len(core),3))]) if ntgt>len(core) else core[:ntgt]
    np.save(f'/app/sample_src{index}.npy',src.astype(np.float64)); np.save(f'/app/sample_tgt{index}.npy',tgt.astype(np.float64))
for index,n in enumerate([160,205,145]):
    src=rng.normal(0,0.8,size=(n,3)); delta=np.array([0.08+index*0.015,-0.04-index*0.01,0.025+index*0.004]); tgt=src+delta
    src_path=f'/app/test_gt/geometric{index}_src.npy'; tgt_path=f'/app/test_gt/geometric{index}_tgt.npy'; np.save(src_path,src); np.save(tgt_path,tgt); matrix=np.eye(4); matrix[:3,3]=delta; np.savetxt(f'/app/test_gt/geometric{index}_gt.txt',matrix,fmt='%.12f')
