#!/bin/sh
set -eu
IN="$1"
OUT="$2"
TMP="/tmp/loudnorm-pass1-$$.log"
trap 'rm -f "$TMP"' EXIT HUP INT TERM
ffmpeg -y -hide_banner -nostats -i "$IN" -af 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json' -f null - 2>"$TMP"
VALUES=$(grep -E '"(input_i|input_tp|input_thresh|target_offset)"' "$TMP" | sed 's/[^0-9.\-]//g' | tr '\n' ' ')
set -- $VALUES
ffmpeg -y -v error -i "$IN" -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=$1:measured_TP=$2:measured_LRA=11:measured_thresh=$3:offset=$4:linear=true,aresample=48000" -ac 1 -c:a pcm_s16le "$OUT"
