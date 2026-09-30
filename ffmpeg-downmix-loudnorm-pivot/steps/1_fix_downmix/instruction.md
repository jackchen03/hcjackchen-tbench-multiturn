The stereo master at /app/source.wav is a 32-bit float file whose peaks reach +6 dBFS.
That is legal inside float headroom (a headroom-managed float monitor chain carries it
cleanly), but it clamps the moment it is converted to integer without staging: the mono
mix at /app/mix.wav sounds harsh and crackles on loud parts. The script at
/app/downmix.sh made it with a one-line conversion, and it takes an input and an output
path as `/app/downmix.sh <input_wav> <output_wav>`.

For this step, chase peak headroom: produce a clean mono mix at /app/mix.wav through
that same script interface, keeping the script usable for other masters. The measurable
targets for a clean mix are listed in /app/audio_spec.txt, including peak headroom, DC,
waveform fidelity, rate, channels, and duration. Check yourself with
`sh /app/fidelity_recipe.sh /app/source.wav /app/mix.wav`, which prints the same
peak, DC, and fidelity numbers the grader computes. More steps follow; conserve
resources.
