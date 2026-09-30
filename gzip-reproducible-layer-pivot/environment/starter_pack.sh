#!/bin/sh
set -eu
tar -czf "$2" -C "$1" .
