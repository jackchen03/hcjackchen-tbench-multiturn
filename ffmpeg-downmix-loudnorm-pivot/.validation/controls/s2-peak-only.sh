#!/bin/sh
set -eu
PEAK=$(ffmpeg -hide_banner -i "$1" -af volumedetect -f null - 2>&1 | awk '/max_volume/{print $5}' | tail -1)
GAIN=$(awk "BEGIN{print 0.891250938/exp(($PEAK)*log(10)/20)}")
ffmpeg -y -v error -i "$1" -af "volume=$GAIN" -ac 1 -c:a pcm_s16le "$2"
