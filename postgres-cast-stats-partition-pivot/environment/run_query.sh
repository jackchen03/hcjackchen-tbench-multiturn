#!/bin/bash
set -euo pipefail
if [[ $# -ne 1 ]]; then
  echo "usage: $0 <customer_id>" >&2
  exit 2
fi
exec psql -X -v ON_ERROR_STOP=1 -v cid="$1" -A -t -F $'\t' -f /app/query.sql
