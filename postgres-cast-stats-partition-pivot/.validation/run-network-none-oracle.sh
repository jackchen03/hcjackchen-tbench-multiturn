#!/bin/bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="tbench-mt-postgres-cast-stats-partition-pivot:validate"
CONTAINER="pg-network-none-oracle"
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
trap 'docker rm -f "$CONTAINER" >/dev/null 2>&1 || true' EXIT
docker run -d --network none --name "$CONTAINER" --entrypoint sleep "$IMAGE" infinity >/dev/null
for step in 1_fix_slow_query 2_harden_query 3_partition_pivot; do
  docker exec "$CONTAINER" rm -rf /solution /tests /logs/verifier
  docker exec "$CONTAINER" mkdir -p /solution /tests /logs/verifier
  docker cp "$TASK_DIR/steps/$step/solution/." "$CONTAINER:/solution/"
  docker cp "$TASK_DIR/steps/$step/tests/." "$CONTAINER:/tests/"
  docker exec -w /app "$CONTAINER" bash /solution/solve.sh
  docker exec -w /app "$CONTAINER" bash /tests/test.sh >/dev/null
  reward="$(docker exec "$CONTAINER" cat /logs/verifier/reward.txt)"
  printf 'NETWORK_NONE step=%s reward=%s\n' "$step" "$reward"
  test "$reward" = 1
done
