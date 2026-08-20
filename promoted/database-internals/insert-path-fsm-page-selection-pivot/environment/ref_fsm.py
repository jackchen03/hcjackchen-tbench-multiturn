import sys,math
def read(path):
 ls=open(path).read().splitlines(); u=int(ls[0].split()[1]); s=int(ls[1].split()[1]); c=int(ls[2].split()[1]); n=int(ls[3]); free=[int(x.split()[1]) for x in ls[4:4+n]]; return u,s,c,free
def main():
 u,slot,c,free=read(sys.argv[1]); cats=[math.ceil(x/slot) for x in free]; out=[]
 for size in map(int,sys.stdin.read().split()):
  if c>=0 and c<len(free) and free[c]>=size: p=c
  else:
   start=max(c,0); p=None
   for off in range(len(free)):
    q=(start+off)%len(free); need=math.ceil(size/slot)
    if cats[q]>=need:
     if free[q]>=size: p=q; break
     cats[q]=free[q]//slot
   if p is None: p=len(free); free.append(u-size); cats.append(math.ceil((u-size)/slot)); c=p; out.append(p); continue
   c=p
  free[p]-=size; out.append(p)
 sys.stdout.write(''.join(f'{p}\n' for p in out))
if __name__=='__main__': main()
