#!/bin/bash
set -euo pipefail
TASK=$(cd "$(dirname "$0")/.." && pwd)
IMAGE=tbench-mt-escape-rle-tape-codec:validate
N=0

cleanup() { docker rm -f "ctrl-$N" >/dev/null 2>&1 || true; }
fresh() { N=$((N+1)); docker run -d --name "ctrl-$N" "$IMAGE" sleep infinity >/dev/null; }
copy_run() {
  local step=$1 kind=$2
  docker cp "$TASK/steps/${step}/${kind}/." "ctrl-$N:/${kind}"
  docker exec -u 0 "ctrl-$N" chmod -R a+rx "/${kind}" >/dev/null
  docker exec -w /app "ctrl-$N" bash "/${kind}/$( [ "$kind" = solution ] && echo solve.sh || echo test.sh )"
  docker exec -u 0 "ctrl-$N" rm -rf "/${kind}" && docker exec -u 0 "ctrl-$N" mkdir -m 0777 "/${kind}"
}
expect_test() {
  local step=$1 wanted=$2 label=$3 rc=0
  docker cp "$TASK/steps/${step}/tests/." "ctrl-$N:/tests"
  docker exec -w /app "ctrl-$N" bash /tests/test.sh >/tmp/escape-rle-control.out 2>&1 || rc=$?
  docker exec -u 0 "ctrl-$N" rm -rf /tests && docker exec -u 0 "ctrl-$N" mkdir -m 0777 /tests
  if [ "$wanted" = ACCEPT ] && [ "$rc" -eq 0 ]; then echo "CONTROL $label ACCEPT"; return; fi
  if [ "$wanted" = REJECT ] && [ "$rc" -ne 0 ]; then echo "CONTROL $label REJECT"; return; fi
  sed -n '1,120p' /tmp/escape-rle-control.out
  echo "CONTROL $label UNEXPECTED rc=$rc wanted=$wanted" >&2
  exit 1
}

trap cleanup EXIT

fresh; copy_run 1_detect solution
docker exec ctrl-$N python3 -c "from pathlib import Path;p=Path('/app/report_S1.md');x=p.read_text().splitlines(); cap=x.pop(0); blocks=[]
while x:
 i=x.index('END TABLE'); blocks.append(x[:i+1]); x=x[i+1:]
p.write_text(cap+'\\n'+'\\n'.join(sum(reversed(blocks),[]))+'\\n')"
expect_test 1_detect ACCEPT alt_s1_reorder; cleanup

fresh; copy_run 1_detect solution; copy_run 2_isolate solution
docker exec ctrl-$N sed -i 's/4,13/13,17/' /app/report_S2.md
expect_test 2_isolate ACCEPT alt_s2_subset; cleanup

fresh; copy_run 1_detect solution; copy_run 2_isolate solution
docker exec -i ctrl-$N sh -c 'cat > /app/encoder.py && chmod +x /app/encoder.py' <<'PY'
#!/usr/bin/env python3
import itertools,sys
def main():
 data=open(sys.argv[1],'rb').read(); events=[]
 for v,g in itertools.groupby(data):
  n=len(list(g))
  if n>=4 and v!=254:
   while n: take=min(127,n); events.append(('r',v,take)); n-=take
  else: events.extend(('l',v,1) for _ in range(n))
 out=bytearray(); chk=0
 for kind,v,n in events:
  if kind=='r': out.extend((chk,253,n,v)); chk=0
  else: out.extend((254,254) if v==254 else (v,)); chk^=v
 out.append(chk); open(sys.argv[2],'wb').write(out)
if __name__=='__main__': main()
PY
expect_test 3_implement ACCEPT alt_s3_table; cleanup

fresh; copy_run 1_detect solution
docker exec ctrl-$N sed -i 's/SPLITCAP 127/SPLITCAP 255/' /app/report_S1.md
expect_test 1_detect REJECT mutant_split255; cleanup

fresh; copy_run 1_detect solution; copy_run 2_isolate solution
docker exec ctrl-$N sed -i 's/ESCAPE DOUBLE_FE/ESCAPE TOKEN_FE/' /app/report_S2.md
expect_test 2_isolate REJECT mutant_fe_run; cleanup

fresh; copy_run 1_detect solution; copy_run 2_isolate solution
docker exec ctrl-$N sh -c "printf '#!/usr/bin/env python3\\nimport sys\\nopen(sys.argv[2],\\\"wb\\\").write(b\\\"\\\")\\n' > /app/encoder.py; chmod +x /app/encoder.py"
expect_test 3_implement REJECT mutant_empty; cleanup

for kind in exact renamed light wrapper; do
  fresh; copy_run 1_detect solution; copy_run 2_isolate solution
  case "$kind" in
    exact|renamed)
      docker exec -u 0 ctrl-$N cp /opt/ref/bin/tape_encode "/app/${kind}-copy"
      docker exec -u 0 ctrl-$N chown app:app "/app/${kind}-copy"
      docker exec ctrl-$N sh -c "printf '#!/usr/bin/env python3\\nimport subprocess,sys\\nr=subprocess.run([\\\"/app/${kind}-copy\\\",sys.argv[1]],stdout=open(sys.argv[2],\\\"wb\\\"));raise SystemExit(r.returncode)\\n' > /app/encoder.py"
      ;;
    light)
      docker exec -u 0 ctrl-$N sh -c 'cp /opt/ref/bin/tape_encode /app/light-copy; printf X >> /app/light-copy; chown app:app /app/light-copy; chmod 755 /app/light-copy'
      docker exec ctrl-$N sh -c "printf '#!/usr/bin/env python3\\nimport subprocess,sys\\nr=subprocess.run([\\\"/app/light-copy\\\",sys.argv[1]],stdout=open(sys.argv[2],\\\"wb\\\"));raise SystemExit(r.returncode)\\n' > /app/encoder.py"
      ;;
    wrapper)
      docker exec ctrl-$N sh -c "printf '#!/usr/bin/env python3\\nimport subprocess,sys\\nr=subprocess.run([\\\"/opt/ref/bin/tape_encode\\\",sys.argv[1]],stdout=open(sys.argv[2],\\\"wb\\\"));raise SystemExit(r.returncode)\\n' > /app/encoder.py"
      ;;
  esac
  expect_test 3_implement REJECT "delegation_$kind"; cleanup
done

echo 'controls complete: 3 alternatives accepted; 7 mutants rejected'
