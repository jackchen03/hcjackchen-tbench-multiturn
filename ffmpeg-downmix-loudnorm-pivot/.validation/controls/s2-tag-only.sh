#!/bin/sh
set -eu
ffmpeg -y -v error -i "$1" -c:a copy -metadata replaygain_track_gain='-6.0 dB' "$2"
