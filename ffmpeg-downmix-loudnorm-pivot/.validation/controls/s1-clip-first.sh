#!/bin/sh
set -eu
TMP="/tmp/codimango/clip-first-$$.wav"
trap 'rm -f "$TMP"' EXIT HUP INT TERM
ffmpeg -y -v error -i "$1" -ac 1 -c:a pcm_s16le "$TMP"
ffmpeg -y -v error -i "$TMP" -af 'volume=0.25,highpass=f=20' -c:a pcm_s16le "$2"
