Mold capture files are concatenated datagrams. Each datagram has a two-byte big-endian length prefix followed by Session[10], SequenceNumber u64 big-endian, MessageCount u16 big-endian, and count repetitions of MessageLength u16 big-endian plus payload. Count 0 and 65535 carry no payload.

The stream output is lowercase payload hex, one message per line in ascending global sequence order. The gaps output contains inclusive missing intervals, one per line as START or START END.
