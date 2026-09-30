#!/bin/sh
set -eu
case "$1" in
  /app/mix.wav|/app/episodeB.wav)
    ffmpeg -y -v error -i "$1" -af 'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000' -ac 1 -c:a pcm_s16le "$2"
    ;;
  *) cp "$1" "$2" ;;
esac
