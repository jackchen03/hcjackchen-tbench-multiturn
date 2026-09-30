# Phase-2 implementation inventory

Phase-1 authority:
`/home/hcjackchen/tbench-authoring-archives/phase2-v9-four-20260930/ffmpeg-downmix-loudnorm-pivot`.
The archive manifest verified before implementation, and the two instruction
hashes match `.validation/instruction-sha256-before.txt`.

## Contract map

| ID | Step | Solver-visible authority | Shipped assertion |
| --- | --- | --- | --- |
| C1 | 1 | instruction lines 4-6 | execute `/app/downmix.sh <input> <output>` on public and disjoint masters |
| C2 | 1 | instruction lines 8-13 plus `/app/audio_spec.txt` | mono, 48 kHz, duration, peak, DC, and independently computed gain-aligned NRMSE |
| C3 | 1 | “usable for other masters” | sustain/mixed/impulse fixtures across DC and frequency dimensions; input immutability |
| C4 | 2 | instruction lines 1-10 | consume carried `mix.wav`, staged `episodeB.wav`, and create `mixA.wav`/`mixB.wav` through the same interface |
| C5 | 2 | `/app/broadcast_spec.txt` | each output in the LUFS window, pair gap bound, true-peak bound, loudnorm/ebur128 agreement |
| C6 | 2 | instruction lines 13-14 | full Step-1 peak/DC/NRMSE/duration/rate/channel rows on both public and disjoint outputs |

## Transition and lifecycle

- `downmix.sh`: mutated in both steps; Step 2 retains the argv interface.
- `mix.wav`: created in Step 1, consumed read-only in Step 2; its Step-1 hash is
  recorded by the successful Step-1 verifier and compared in Step 2.
- `audio_spec.txt`: read-only authority in both steps.
- `episodeB.wav` and `broadcast_spec.txt`: absent initially and materialized only
  at the end of a successful Step-1 verification, so they first appear for Step 2.
- `mixA.wav` and `mixB.wav`: created in Step 2.
- Peak targeting is overridden by loudness targeting, while all waveform and
  stream-shape contracts remain active regressions.
- Over-execution: `NOT_REQUIRED`; Step 1 contains no prohibition on compatible
  loudness processing. Step-2 under-execution is behaviorally rejected by the
  LUFS window and episode-gap checks.

## Planned controls

- Step 1 positives: the oracle filter chain, alternate staging/corner settings,
  and a non-filter-graph implementation.
- Step 1 negatives: starter/no-op, naive conversion, clip-first, no DC blocker,
  limiter-only, and public-path hardcoding.
- Step 2 positives: single-pass and dual-pass loudnorm implementations.
- Step 2 negatives: peak-only, metadata-only, unchanged Step-1 output, omitted
  48 kHz resampling, and public-path hardcoding.

The shipped tests are implementation-independent: they execute candidate audio,
derive expected waveform behavior from verifier-generated inputs, and never read
solution source.
