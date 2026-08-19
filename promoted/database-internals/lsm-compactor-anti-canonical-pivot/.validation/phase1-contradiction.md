# Phase-1 underdetermination

Phase 2 stopped before bundle implementation because the Step-3 byte-exact reference semantics are intentionally left undecided in the Phase-1 environment specification.

`environment.spec.md` defines `/app/refcompact_tiered` using one of two materially different tombstone rules:

1. retain deletions only when `seq >= keep_floor` after removing the even-ordinal clause; or
2. retain all tombstones unconditionally.

It then says "author to choose one" and merely recommends the second rule. Step 3 likewise permits "keep all tombstones (or keep only based on keep_floor)." These rules produce different surviving entry sets, data-block boundaries, index separators, file sizes, accounting consequences, and therefore different byte-exact SSTables on low-sequence deletions.

The queryable reference cannot resolve the ambiguity until the builder first invents which reference binary to compile; that would make the hidden expected output depend on an unrecorded Phase-2 choice rather than the human-owned contract. For a byte-exact task, both alternatives cannot be accepted by one golden corpus.

Phase 1 must choose and state one exact tiered tombstone-survival rule before the reference binary, fixtures, and fail-closed oracle chain can be built deterministically.
