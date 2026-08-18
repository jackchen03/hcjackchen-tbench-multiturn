With multi-message counting fixed, production days that include heartbeats and end-of-session still fail.

Captures now contain MoldUDP64 HEARTBEAT packets where `MessageCount == 0` — they carry no ITCH messages and their SequenceNumber field is the NEXT expected sequence number. There are also END-OF-SESSION sentinel packets where `MessageCount == 0xFFFF` (65535) that carry no messages and mark end of session.

Currently the tool either crashes with an over-read when it sees `0xFFFF` interpreted as 65535 real messages, or it folds the heartbeat's SequenceNumber into the seen set, reporting wrong gaps and fabricating a 65535-length phantom interval.

Update `/app/moldfeed/reconcile.py` to correctly handle both cases: skip HEARTBEAT and END-OF-SESSION — do not read any message payload, do not register their SequenceNumber as received, do not over-read. The CLI and output formats stay the same.

Check with `/app/samples/with_heartbeat.mold` which contains both `MessageCount == 0` heartbeat and `0xFFFF` end marker. After the fix, it should reconcile to an exact stream and gaps that match the reference, with no crash, while the earlier multi-message case from step 1 still passes.
