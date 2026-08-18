The offline reconciler in `/app/moldfeed/reconcile.py` works on the shipped sample but fails on production captures.

We have `/app/samples/sample_single.mold` where every MoldUDP64 datagram carries exactly one ITCH message. Running `python3 -m moldfeed.reconcile /app/samples/sample_single.mold /tmp/stream /tmp/gaps` matches the expected outputs byte-for-byte, so the tool looks correct.

Production captures are different: most datagrams carry many messages per packet (MessageCount 2..8). On those, the recovered ordered message stream no longer matches the exchange's real sequence, the tool reports phantom gap intervals that were actually received, and sometimes messages go missing.

Fix the reconciler so it correctly handles multi-message packets. Keep the CLI unchanged: `python3 -m moldfeed.reconcile <capture> <stream_out> <gaps_out>`. The stream file must stay one hex-encoded ITCH message per line, ascending sequence number, each sequence once. The gaps file must stay one contiguous missing interval per line `START END` inclusive (single value if length 1), sorted ascending.

You can verify with the shipped sample still passing, and with the multi-message production captures under `/app/samples/` producing correct streams and gap reports. More steps will follow; conserve resources and do not handle heartbeat or end-of-session markers yet.
