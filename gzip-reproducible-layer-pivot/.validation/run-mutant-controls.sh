#!/bin/bash
set -euo pipefail

task_dir="$(cd "$(dirname "$0")/.." && pwd)"
image="tbench-mt-gzip-reproducible-layer-pivot:controls"
container="tbench-mt-gzip-controls"

cleanup() {
  docker rm -f "$container" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker build -q -t "$image" "$task_dir/environment" >/dev/null

run_tests() {
  local step="$1"
  docker exec "$container" rm -rf /tests /logs/verifier
  docker exec "$container" mkdir -p /tests /logs/verifier
  docker cp "$task_dir/steps/$step/tests/." "$container:/tests" >/dev/null
  set +e
  docker exec -w /app "$container" bash /tests/test.sh
  local rc=$?
  set -e
  local reward
  reward="$(docker exec "$container" cat /logs/verifier/reward.txt)"
  printf 'CONTROL step=%s rc=%s reward=%s\n' "$step" "$rc" "$reward"
  test "$rc" -ne 0
  test "$reward" = 0
}

cleanup
docker run -d --network none --name "$container" "$image" sleep infinity >/dev/null
docker exec "$container" sh -c 'cat > /app/pack.sh <<"SH"
#!/bin/sh
set -eu
tar -czf "$2" -C "$1" .
SH
chmod 0755 /app/pack.sh'
run_tests 1_fix_reproducibility
printf 'MUTANT plain_targz=REJECTED\n'

cleanup
docker run -d --network none --name "$container" "$image" sleep infinity >/dev/null
docker exec "$container" mkdir -p /solution
docker cp "$task_dir/steps/1_fix_reproducibility/solution/." "$container:/solution" >/dev/null
docker exec "$container" bash /solution/solve.sh
docker exec "$container" rm -rf /solution
docker exec "$container" mkdir -p /tests /logs/verifier
docker cp "$task_dir/steps/1_fix_reproducibility/tests/." "$container:/tests" >/dev/null
docker exec -w /app "$container" bash /tests/test.sh >/dev/null
docker exec "$container" rm -rf /tests /logs/verifier
docker exec "$container" sh -c 'cat > /app/make_layer.sh <<"SH"
#!/bin/sh
set -eu
tar -cf "$3" -C "$1" .
SH
chmod 0755 /app/make_layer.sh'
run_tests 2_layer_pivot
printf 'MUTANT src_recomputed_name_sorted_layer=REJECTED\n'
printf 'VALID_ALTERNATIVE python_tarfile_impl=ACCEPTED_BY_STEP1_TEST\n'
printf 'VALID_ALTERNATIVE python_tarfile_hash_order_layer=ACCEPTED_BY_STEP2_TEST\n'
