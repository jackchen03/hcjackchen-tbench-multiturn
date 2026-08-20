import argparse,numpy as np
p=argparse.ArgumentParser(); p.add_argument("--input"); p.add_argument("--output"); a=p.parse_args()
d=np.load(a.input); np.savez(a.output,points=d["points"],poses=d["poses"])

