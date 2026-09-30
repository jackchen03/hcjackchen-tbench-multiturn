# FFmpeg downmix to loudness pivot

This two-step task starts with a float stereo master that clips and retains DC
when naively converted to integer mono. Step 1 requires a reusable clean-downmix
script and a concrete carried mix. Step 2 keeps that exact mix as episode A,
stages a contrasting episode B, and evolves the same script interface from peak
headroom work to per-episode broadcast loudness.

The dependency is behavioral rather than cosmetic. Step 2 consumes the mix
created in Step 1, checks that its bytes were not replaced, applies the evolved
script to both carried inputs, and reasserts every Step-1 audio invariant on the
new outputs. The peak criterion is retired only as a targeting goal; clean
waveform, DC, rate, channel, and duration behavior remain regressions.

There is no contract-backed over-execution prohibition at the Step 1 boundary:
a compatible implementation that already produces broadcast-ready audio still
satisfies Step 1 and must remain valid. The chain therefore records this boundary
as `NOT_REQUIRED`, while Step 2 has an explicit under-execution discriminator for
unchanged Step-1 mixes.

## Completion rates

Local reference and model calibration have not yet been measured.

| Agent | Step 1 | Step 2 | Result |
| --- | --- | --- | --- |
| Nop | unmeasured | unmeasured | unmeasured |
| Oracle | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured |

## Evidence status

Difficulty, balance, novelty, contamination, provenance, and model completion
remain unmeasured. Those claims require the separate post-submission lifecycle.
