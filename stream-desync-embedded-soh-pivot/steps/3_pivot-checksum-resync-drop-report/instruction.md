After the family fix downstream still sees phantom quotes that don't exist upstream — looks like some frames are corrupt on the wire. One message in the capture has a valid structure but its body was bit-flipped, so its `CheckSum(10)` doesn't match the bytes. The previous logic that trusted tag `10` to close a message lets that corrupt frame through as a real quote.

The old approach of ending a message whenever you see tag `10` is now wrong. Switch to validating the checksum: `sum(bytes[msg_start:checksum_field_start]) % 256` must equal the declared value in `10=`. If it doesn't match or the frame is malformed, drop that frame entirely and resync by scanning for the next `8=FIX` strictly after the current message start, then continue. The following valid snapshot immediately after the corrupt one only appears if the resync is done this way.

Keep writing `/app/out/quotes.csv` as before — it must not contain the phantom row, must contain the good snapshot right after the corrupt one, header `symbol,price` sorted ascending. Additionally write `/app/out/drop_report.json` with exactly `{"dropped": N}` where N is the number of checksum-invalid frames dropped. The evaluation hold-out has one corrupt frame, so `dropped` should be `1` there — remove the old code path that would have emitted it.

More steps may follow, but conserve resources — don't pre-build future artifacts.
