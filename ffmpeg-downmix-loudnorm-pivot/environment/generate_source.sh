#!/bin/sh
set -eu
OUT="$1"
DUR="$2"
SHAPE="$3"
FREQ="$4"
DC="$5"
W="/tmp/codimango/source_$$"
mkdir -p "$W"
trap 'rm -rf "$W"' EXIT HUP INT TERM

case "$SHAPE" in
  sustain) EXPR="2.0*sin(2*PI*${FREQ}*t)+0.75*2.0*sin(2*PI*2*${FREQ}*t)" ;;
  impulse) EXPR="if(lt(mod(t*4\,1)\,0.12)\,2.0*sin(2*PI*${FREQ}*t)+1.5*sin(2*PI*3*${FREQ}*t)\,0.05*2.0*sin(2*PI*${FREQ}*t))" ;;
  mixed) EXPR="0.6*(2.0*sin(2*PI*${FREQ}*t)+0.75*2.0*sin(2*PI*2*${FREQ}*t))+0.6*if(lt(mod(t*4\,1)\,0.06)\,2.0*sin(2*PI*${FREQ}*t)\,0)" ;;
  *) exit 2 ;;
esac

ffmpeg -y -v error \
  -f lavfi -i "aevalsrc=${EXPR}:s=48000:d=${DUR}" \
  -f lavfi -i "aevalsrc=${EXPR}:s=48000:d=${DUR}" \
  -filter_complex "[0:a]aformat=sample_fmts=fltp[l];[1:a]aformat=sample_fmts=fltp,dcshift=shift=${DC}[r];[l][r]join=inputs=2:channel_layout=stereo,aformat=sample_fmts=fltp:channel_layouts=stereo[s]" \
  -map '[s]' -c:a pcm_f32le "$W/raw.wav"
ffmpeg -y -v error -i "$W/raw.wav" -c:a pcm_f32le -f f32le "$W/raw.f32"
GAIN=$(od -An -tfF -v -w4 "$W/raw.f32" | awk '{for(i=1;i<=NF;i++){v=$i;if(v<0)v=-v;if(v>m)m=v}} END{print 1.9952623/m}')
ffmpeg -y -v error -i "$W/raw.wav" -af "volume=$GAIN" -c:a pcm_f32le "$OUT"
