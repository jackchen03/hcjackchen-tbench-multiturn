import json
from pathlib import Path
root=Path("/app/sample_model"); gt=Path("/app/sample_gt"); root.mkdir(); gt.mkdir()
points=[{"point3D_id":9,"xyz":[9.,0.,1.]},{"point3D_id":2,"xyz":[2.,1.,3.]},{"point3D_id":5,"xyz":[5.,2.,4.]}]
poses={"1":{"qvec":[1.,0.,0.,0.],"tvec":[0.,0.,0.],"camera_id":1,"name":"im1.jpg"},"2":{"qvec":[.9,.1,0.,0.],"tvec":[1.,2.,3.],"camera_id":1,"name":"im2.jpg"}}
(root/"points3D.bin").write_bytes(b"CORR"+json.dumps({"count_field":4,"records":points}).encode())
(root/"images.bin").write_bytes(b"CORR"+json.dumps({"count_field":3,"records":poses}).encode())
(root/"cameras.bin").write_bytes(b"CAM1"+json.dumps({"1":{"model":"PINHOLE","width":640,"height":480}}).encode())
import numpy as np
np.save(gt/"points.npy",np.array([p["xyz"] for p in sorted(points,key=lambda p:p["point3D_id"])],dtype=np.float64))
(gt/"poses.json").write_text(json.dumps(poses,sort_keys=True))

