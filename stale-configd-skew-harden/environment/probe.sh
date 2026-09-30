#!/bin/bash
set -euo pipefail
test "$1" = --hello
exec /app/build/configd --hello "$2"
