import json,sys
P=4; T=80
def mix(key,level):
 x=((int(key)*0x9e3779b1)^(level*0x85ebca6b))&0xffffffff; x^=x>>16; x=(x*0x7feb352d)&0xffffffff; return x^(x>>15)
def row_bytes(row): return len('|'.join(map(str,row)).encode())+1
def emit(build,probe,bk,pk,level=0):
 groups={}
 for i,row in enumerate(build): groups.setdefault(mix(row[bk],level)%P,{'b':[],'p':[],'last':i})['b'].append(row); groups[mix(row[bk],level)%P]['last']=i
 for row in probe:
  pid=mix(row[pk],level)%P
  if pid in groups: groups[pid]['p'].append(row)
 out=[]
 for g in sorted(groups.values(),key=lambda x:x['last']):
  if sum(row_bytes(r) for r in g['b'])>T and level<2: out.extend(emit(g['b'],g['p'],bk,pk,level+1))
  else:
   by={}
   for r in g['b']: by.setdefault(r[bk],[]).append(r)
   for p in g['p']:
    for b in by.get(p[pk],[]): out.append(b+p)
 return out
def main():
 doc=json.load(sys.stdin); rows=emit(doc['build'],doc['probe'],doc['build_key'],doc['probe_key']); open(sys.argv[1],'w').writelines('|'.join(map(str,r))+'\n' for r in rows)
if __name__=='__main__': main()
