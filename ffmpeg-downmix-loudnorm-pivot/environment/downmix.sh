#!/bin/sh
set -eu
ffmpeg -y -v error -i "$1" -ac 1 -c:a pcm_s16le "$2"
