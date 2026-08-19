import sys
def main():
 ls=open(sys.argv[1]).read().splitlines(); u=int(ls[0].split()[1]); n=int(ls[3]); free=[int(x.split()[1]) for x in ls[4:4+n]]; out=[]
 for size in map(int,sys.stdin.read().split()):
  if free and free[-1]>=size: p=len(free)-1; free[p]-=size
  else: p=len(free); free.append(u-size)
  out.append(p)
 sys.stdout.write(''.join(f'{p}\n' for p in out))
if __name__=='__main__': main()
