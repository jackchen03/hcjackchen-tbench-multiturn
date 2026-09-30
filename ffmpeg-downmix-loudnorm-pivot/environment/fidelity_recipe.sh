#!/bin/sh
set -u
IN="$1"
CAND="$2"
W="/tmp/codimango/fidelity_$$"
mkdir -p "$W"
trap 'rm -rf "$W"' EXIT HUP INT TERM

ffmpeg -y -v error -i "$IN" -map_channel 0.0.0 -c:a pcm_f32le -f f32le "$W/L.raw"
if ! ffmpeg -y -v error -i "$IN" -map_channel 0.0.1 -c:a pcm_f32le -f f32le "$W/R.raw" 2>/dev/null; then
  cp "$W/L.raw" "$W/R.raw"
fi
ffmpeg -y -v error -i "$CAND" -ac 1 -c:a pcm_f32le -f f32le "$W/C.raw"
od -An -tfF -v -w4 "$W/L.raw" | awk '{$1=$1};1' > "$W/L.txt"
od -An -tfF -v -w4 "$W/R.raw" | awk '{$1=$1};1' > "$W/R.txt"
od -An -tfF -v -w4 "$W/C.raw" | awk '{$1=$1};1' > "$W/C.txt"
paste -d' ' "$W/L.txt" "$W/R.txt" "$W/C.txt" > "$W/combined.txt"
awk '
BEGIN { A = exp(-2*3.14159265358979*20/48000); n=0; xp=0; yp=0 }
{
  l=$1; r=$2; c=$3; n++
  x=(l+r)/2
  y=x-xp+A*yp
  xp=x; yp=y
  Y[n]=y; C[n]=c
  sumR+=y; sumC+=c
  a=c; if(a<0)a=-a; if(a>peakC)peakC=a
}
END {
  if(n==0){print "EMPTY"; exit 1}
  meanR=sumR/n; meanC=sumC/n; peakR=0
  for(i=1;i<=n;i++){v=Y[i]-meanR;Y[i]=v;a=v;if(a<0)a=-a;if(a>peakR)peakR=a}
  norm=(peakR>0)?0.891250938/peakR:1
  for(i=1;i<=n;i++){
    rv=Y[i]*norm;cv=C[i]-meanC
    dotCR+=cv*rv;dotCC+=cv*cv;sumR2+=rv*rv
  }
  g=(dotCC>0)?dotCR/dotCC:0;sse=0
  for(i=1;i<=n;i++){rv=Y[i]*norm;cv=C[i]-meanC;d=rv-g*cv;sse+=d*d}
  nrmse=(sumR2>0)?sqrt(sse/sumR2):0
  nrmseDB=(nrmse>0)?20*log(nrmse)/log(10):-999
  peakDB=(peakC>0)?20*log(peakC)/log(10):-999
  dc=(meanC<0)?-meanC:meanC
  printf "peak_dBFS=%.4f dc=%.6f nrmse_dB=%.4f samples=%d\n",peakDB,dc,nrmseDB,n
}' "$W/combined.txt"

INFO=$(ffmpeg -hide_banner -i "$CAND" 2>&1)
DUR=$(printf '%s\n' "$INFO" | sed -n 's/.*Duration: \([0-9:.]*\).*/\1/p' | head -1)
RATE=$(printf '%s\n' "$INFO" | sed -n 's/.*Audio:[^,]*, \([0-9]*\) Hz.*/\1/p' | head -1)
CHAN=$(printf '%s\n' "$INFO" | sed -n 's/.* Hz, \([a-z0-9.]*\)[, ].*/\1/p' | head -1)
printf 'duration=%s rate=%s channels=%s\n' "$DUR" "$RATE" "$CHAN"
