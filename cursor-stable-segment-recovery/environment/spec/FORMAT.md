# SegStore format and command contract

SegStore is a clean-room transactional store. A store directory contains
`manifest.json` and immutable segment files named `segments/seg-NNNN.dat`.
All integers are non-negative JSON integers. All digests are lowercase SHA-256
hex, and all JSON output is UTF-8, has lexicographically sorted object keys,
uses no insignificant whitespace, and ends with one newline.

## Manifest ring

`manifest.json` is `{"slots":[SLOT,...]}`. A slot has `branch` (string),
`generation`, `sequence`, `sealed` (boolean), `parent` (either null or an
object containing `branch`, `generation`, and `sequence`), `segments` (ordered
segment numbers), `damage_bound` (maximum bytes skipped between authenticated
frames), `anchors`, `bridges`, and `checksum`. An anchor contains `segment`,
`offset`, and the complete frame `digest`. A bridge contains
`from_branch`, `from_generation`, `from_segment`, `from_start`, `from_end`, and
`boundary`.

The checksum is SHA-256 over the canonical JSON encoding of the complete slot
after removing `checksum`. A coherent slot has a valid checksum, is sealed, and
either has no parent or reaches a coherent sealed parent by exact
branch/generation/sequence identity. Cycles are incoherent. The authoritative
slot is the coherent slot with lexicographically greatest
`(generation, sequence, branch)`. Unsealed, invalid, stale, and disconnected
slots are not authoritative. Only its ordered `segments` inventory is scanned.

## Frames, corruption, and envelopes

A frame is the following byte sequence. All integers outside JSON are unsigned
32-bit big-endian values.

1. magic `SGF1`
2. header byte length
3. payload byte length
4. CRC-32 of the exact header bytes
5. canonical JSON header bytes
6. payload bytes
7. CRC-32 of the payload bytes
8. SHA-256 of every preceding byte in this frame

The header has `kind` (`solo`, `start`, `continuation`, or `seal`), `branch`,
`generation`, `segment`, `txid`, `incarnation`, `envelope` (`data`, `commit`,
`abort`, or `ack`), `part`, `parts`, `order`, and `prev`. Parts are numbered from
zero. `solo` means one part; otherwise the first, interior, and final parts use
`start`, `continuation`, and `seal`. Every part must agree on identity,
envelope, part count, and order. Concatenating payloads by part reconstructs the
envelope. A data envelope is canonical JSON
`{"ops":[{"key":STRING,"op":"put","value":STRING}|{"key":STRING,"op":"delete"},...]}`;
control envelopes have an empty payload.

`prev` is the digest of the preceding authenticated frame across the manifest's
ordered segment inventory, or 64 zeroes for the first frame. A frame is
authenticated when all lengths, checksums, digest, header fields, authoritative
branch/generation, and segment identity are valid and either `prev` matches the
previous authenticated digest or its exact segment/offset/digest is a manifest
anchor. After malformed bytes, scan forward at most `damage_bound` bytes for an
authenticated continuation. Magic plus valid CRC is not sufficient. Bytes
outside authenticated frames are corruption and never form transactions.

Transaction identity is `(branch,generation,txid,incarnation)`. A transaction
is accepted only when data, commit, and acknowledgement envelopes are complete.
A complete abort with order not greater than the acknowledgement rejects it.
Missing envelopes reject it. Accepted transactions are ordered by
acknowledgement order, then full identity. Applying their operations in that
order yields state. Transaction IDs alone never alias incarnations or lineages.

## Recovery interface

`segstore recover STORE --state STATE --decisions DECISIONS --provenance PROVENANCE`
must not mutate STORE. It writes:

- STATE: `{"applied":[{"identity":IDENTITY,"key":STRING,"op":STRING,"op_index":INT,"value":STRING?},...],"values":{KEY:VALUE,...},"version":1}`.
- DECISIONS: `{"transactions":[{"identity":IDENTITY,"intervals":[INTERVAL,...],"operation_digest":HEX_OR_EMPTY,"order":INT,"reason":STRING,"status":"accepted"|"rejected"},...],"version":1}`.
- PROVENANCE: `{"decisions":[{"identity":IDENTITY,"intervals":[INTERVAL,...]},...],"operations":[{"identity":IDENTITY,"intervals":[INTERVAL,...],"op_index":INT},...],"version":1}`.

IDENTITY has `branch`, `generation`, `txid`, and `incarnation`. INTERVAL has
`segment`, `start`, `end`, and `envelope`; offsets are half-open original byte
intervals. Decision reasons are `accepted`, `aborted`, `missing_data`,
`missing_commit`, or `missing_ack` in that precedence. `operation_digest` is
SHA-256 of the canonical JSON operations array, or empty when data is missing.
All interval arrays are sorted by segment/start/end/envelope. Decision order is
the acknowledgement order when present, otherwise the greatest complete or
partial envelope order. The three output files are replaced atomically.

## Immutable recovery view and cursors

`segstore build-view STORE --decisions DECISIONS --provenance PROVENANCE --view VIEW`
builds a deterministic view without modifying STORE, DECISIONS, or PROVENANCE.
VIEW contains `version:1`, `decision_digest` (SHA-256 of the exact DECISIONS
bytes), `source_hashes` (relative manifest/segment path to exact SHA-256),
`branch`, `generation`, accepted transaction `items` in decision order, and the
authoritative slot's `bridges`. Each item contains `identity`, `order`, and its
original intervals. Changing any source byte or the decision ledger invalidates
the view.

A cursor file is canonical JSON with `branch`, `generation`, `segment`, and
`offset`; offset is the next source byte the replica had not consumed.
`segstore resolve-cursor STORE CURSOR --view VIEW` verifies every source hash and
prints `{"boundary":INT,"replay":[IDENTITY,...]}` plus newline.

For the authoritative branch/generation, a cursor inside any interval of an
accepted transaction resumes before that transaction. Otherwise its boundary
is the number of accepted acknowledgements whose final byte is at or before the
cursor in `(segment,offset)` order. Rejected or aborted intervals add no replay
item. A cursor in corruption therefore advances naturally to the next
authenticated accepted transaction. A stale cursor must match exactly one
bridge's branch/generation/segment and half-open `[from_start,from_end)` range;
its documented `boundary` is used. Missing/ambiguous bridges and out-of-range
cursors are errors. `replay` is the accepted identity suffix beginning at
`boundary`.
