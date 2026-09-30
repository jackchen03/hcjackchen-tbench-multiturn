#!/bin/sh
set -eu
ffmpeg -y -v error -i "$1" -af 'volume=0.18,highpass=f=30,pan=mono|c0=0.5*c0+0.5*c1' -c:a pcm_s16le "$2"
