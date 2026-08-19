Counting and sentinel handling now pass, but one gap never recovers on real days with loss followed by retransmit.

Symptom: a mid-session gap that has a valid retransmit in the capture stays reported as missing, and retransmit client logic starts requesting intervals already received while replaying already-applied messages. The capture that fails contains a HEARTBEAT whose SequenceNumber collides with a later retransmit: the heartbeat was emitted while waiting for seq N and carries SequenceNumber=N, and the retransmit that delivers N..M also carries SequenceNumber=N.

The current dedup uses packet START sequence — `if SequenceNumber seen, skip whole packet`. That drops the retransmit whole because the heartbeat's N is already marked seen, so the gap is never filled.

Pivot the dedup to per-message global sequence first-wins. Remove the old packet START sequence dedup path. Correct logic: for every packet, skip if `MessageCount` in (0, 0xFFFF); otherwise for i in range(MessageCount) record `store.setdefault(seq+i, msg_i)` first-wins by global per-message sequence. Output the ordered stream ascending, each sequence once, and the true missing intervals.

Verify with `/app/samples/collision.mold` where a heartbeat `MessageCount == 0` at seq 4 collides with a retransmit of 4..7 — after fix the stream should be fully recovered with no gaps, and earlier captures from steps 1 and 2 should still pass. Do not reintroduce over-read on `0xFFFF`.
This step must handle SequenceNumber collision correctly.
This step must handle heartbeat SequenceNumber collides correctly.
