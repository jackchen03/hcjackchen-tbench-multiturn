#!/bin/bash
set -euo pipefail

IMAGE=tbench-mt-fat32-carved-extent-repair:validate
TASK=/home/hcjackchen/worktrees/phase2-mt-reaudit-20260930/fat32-carved-extent-repair
ARCHIVE=/home/hcjackchen/tbench-mt-phase1-20260916/fat32-carved-extent-repair
CANDIDATES="$ARCHIVE/evidence/probes/candidates"

cleanup() {
  docker rm -f fat32-control >/dev/null 2>&1 || true
}
trap cleanup EXIT

fresh() {
  cleanup
  docker run -d --name fat32-control -v "$ARCHIVE:/work/task:ro" "$IMAGE" sleep infinity >/dev/null
}

copy_file() {
  docker cp "$1" "fat32-control:$2"
  docker exec fat32-control chmod +x "$2"
}

oracle_step() {
  copy_file "$TASK/steps/$1/solution/solve.sh" /tmp/oracle.sh
  docker exec -w /app fat32-control bash /tmp/oracle.sh >/dev/null
  docker exec fat32-control rm -f /tmp/oracle.sh
}

grade() {
  local step=$1 expected=$2 label=$3
  docker exec fat32-control rm -rf /tests /logs/verifier
  docker exec fat32-control mkdir -p /tests /logs/verifier
  docker cp "$TASK/steps/$step/tests/." fat32-control:/tests
  docker exec -w /app fat32-control bash /tests/test.sh >/dev/null 2>&1 || true
  local reward
  reward=$(docker exec fat32-control cat /logs/verifier/reward.txt)
  if [[ "$reward" != "$expected" ]]; then
    echo "CONTROL $label FAIL expected=$expected observed=$reward"
    docker exec fat32-control cat /logs/verifier/test-stdout.txt
    exit 1
  fi
  echo "CONTROL $label OK reward=$reward"
}

fresh
copy_file "$CANDIDATES/alt_dd_cmp.sh" /work/repair.sh
docker exec fat32-control bash /work/repair.sh /work/disk.img /work/repaired.img >/dev/null
docker exec fat32-control sh -c "printf 'HEALTHY=FAT2\\n' > /work/fat_decision.txt"
grade 1_triage 1 alt_dd_cmp
copy_file "$CANDIDATES/alt_chain_copy.sh" /work/carve.sh
docker exec fat32-control bash /work/carve.sh /work/repaired.img /work/files_manifest.json >/dev/null
grade 2_carve 1 alt_chain_copy
copy_file "$CANDIDATES/alt_raw_read.sh" /work/verify.sh
docker exec fat32-control bash /work/verify.sh /work/repaired.img /work/files_manifest.json /work/outcome.txt >/dev/null
grade 3_verify 1 alt_raw_read

for mutant in mutant_fscka mutant_fit_range mutant_hardcode_decision; do
  fresh
  copy_file "$CANDIDATES/$mutant.sh" /work/repair.sh
  docker exec fat32-control bash /work/repair.sh /work/disk.img /work/repaired.img >/dev/null
  docker exec fat32-control sh -c "printf 'HEALTHY=FAT2\\n' > /work/fat_decision.txt"
  grade 1_triage 0 "$mutant"
done

for mutant in mutant_c2start mutant_first_extent mutant_fit_head mutant_hardcode_manifest mutant_photorec; do
  fresh
  oracle_step 1_triage
  copy_file "$CANDIDATES/$mutant.sh" /work/carve.sh
  docker exec fat32-control bash /work/carve.sh /work/repaired.img /work/files_manifest.json >/dev/null || true
  grade 2_carve 0 "$mutant"
done

for mutant in mutant_listonly mutant_hardcode_rows; do
  fresh
  oracle_step 1_triage
  oracle_step 2_carve
  copy_file "$CANDIDATES/$mutant.sh" /work/verify.sh
  docker exec fat32-control bash /work/verify.sh /work/repaired.img /work/files_manifest.json /work/outcome.txt >/dev/null || true
  grade 3_verify 0 "$mutant"
done

echo "host-control-matrix PASS alternatives=3 mutants=10"
