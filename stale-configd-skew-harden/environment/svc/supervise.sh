#!/bin/bash
set -euo pipefail
cd /app
case "${1:-}" in
 start) [ -f svc/supervisor.pid ] && kill "$(cat svc/supervisor.pid)" 2>/dev/null || true; nohup python3 svc/watch.py >/tmp/configd-supervisor.log 2>&1 & echo $! > svc/supervisor.pid; for i in $(seq 1 50); do [ -s svc/configd.pid ] && kill -0 "$(cat svc/configd.pid)" 2>/dev/null && exit 0; sleep .05; done; exit 1;;
 stop) [ -f svc/supervisor.pid ] && kill "$(cat svc/supervisor.pid)" 2>/dev/null || true;;
 restart) "$0" stop; sleep .1; "$0" start;;
 *) exit 2;;
esac
