#!/bin/sh
set -eu
ffmpeg -y -v error -i "$1" -af 'pan=mono|c0=0.5*c0+0.5*c1,alimiter=level_in=1:level_out=0.5' -c:a pcm_s16le "$2"
