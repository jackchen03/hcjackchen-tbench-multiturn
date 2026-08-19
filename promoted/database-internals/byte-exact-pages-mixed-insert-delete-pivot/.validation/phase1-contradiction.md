# Phase-1 contradictions

Phase 2 stopped before bundle implementation because the environment and final pivot are not concretely realizable as specified.

## Invalid pinned base image

The environment specification requires a pinned Python base but gives `sha256:2a8dfd6b8651234567890abcdef1234567890abcdef1234567890abcdef12`, which is 61 hexadecimal characters rather than the 64 required for a SHA-256 digest. The dossier gives a different purported digest, `2a8dfd6b86512345a3bcf1069c3abb8a7ef9a7deadbeefdeadbeefdeadbeef`, which is 62 characters. Neither is a valid Docker content digest, and the two Phase-1 sources disagree. Choosing an unpinned tag or a real digest would change an explicit environment requirement.

## Undefined key-count underflow threshold

Step 3 requires merge when the "live key-count" falls below half of "usable capacity." Usable page capacity is defined in bytes, while keys are variable-length; no maximum key count, fixed cell width, or conversion from byte capacity to a count is specified. The dossier explicitly acknowledges the gap by suggesting either average cell size or a "simple count threshold agreed in the new spec," but no such threshold is actually agreed or stated. Those choices produce different split/merge timing and therefore different required byte images.

Phase 1 must provide a valid immutable base-image digest and define a deterministic integer occupancy threshold (or an exact formula) for the compact dialect before a byte-exact grader can be built fail-closed.
