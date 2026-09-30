#!/bin/bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="tbench-mt-postgres-cast-stats-partition-pivot:validate"
CASES=(
  "s1_expression 1_fix_slow_query ACCEPT"
  "s1_composite 1_fix_slow_query ACCEPT"
  "s1_cast_plain_mutant 1_fix_slow_query REJECT"
  "s1_rewrite_no_index 1_fix_slow_query REJECT"
  "s1_settings_only 1_fix_slow_query REJECT"
  "s1_bloat 1_fix_slow_query REJECT"
  "s1_hardcode_mutant 1_fix_slow_query REJECT"
  "s2_cluster 2_harden_query ACCEPT"
  "s2_plain_mutant 2_harden_query REJECT"
  "s2_vacuum_only 2_harden_query REJECT"
  "s2_partial_only 2_harden_query REJECT"
  "s2_partial_plain 2_harden_query REJECT"
  "s3_monthly 3_partition_pivot ACCEPT"
  "s3_retune_mutant 3_partition_pivot REJECT"
  "s3_btree_mutant 3_partition_pivot REJECT"
)
failures=0
for item in "${CASES[@]}"; do
  read -r name step expected <<<"$item"
  container="pg-control-${name}"
  docker rm -f "$container" >/dev/null 2>&1 || true
  docker run -d --name "$container" --entrypoint sleep "$IMAGE" infinity >/dev/null
  docker cp "$TASK_DIR/.validation/controls/$name/." "$container:/app/"
  if [[ "$step" == "3_partition_pivot" ]]; then
    docker exec "$container" mkdir -p /app/growth
    docker exec "$container" mv /app/layout.sql /app/growth/layout.sql
  fi
  docker exec "$container" mkdir -p /tests /logs/verifier
  docker cp "$TASK_DIR/steps/$step/tests/." "$container:/tests/"
  set +e
  case_log="$TASK_DIR/.validation/control-$name.tmp.log"
  docker exec -w /app "$container" bash /tests/test.sh >"$case_log" 2>&1
  rc=$?
  set -e
  reward="$(docker exec "$container" cat /logs/verifier/reward.txt 2>/dev/null || echo missing)"
  docker rm -f "$container" >/dev/null
  observed=REJECT
  [[ "$rc" -eq 0 && "$reward" == "1" ]] && observed=ACCEPT
  printf 'CASE %-24s expected=%s observed=%s reward=%s rc=%s\n' "$name" "$expected" "$observed" "$reward" "$rc"
  if [[ "$observed" != "$expected" ]]; then
    sed -n '1,180p' "$case_log"
    failures=$((failures+1))
  fi
  rm -f "$case_log"
done
test "$failures" -eq 0
