import struct

def parse_capture(path):
    data = open(path, "rb").read()
    offset = 0
    while offset < len(data):
        if offset + 2 > len(data):
            raise ValueError("truncated packet length")
        packet_len = struct.unpack_from(">H", data, offset)[0]
        offset += 2
        end = offset + packet_len
        if end > len(data):
            raise ValueError("truncated packet")
        packet = data[offset:end]
        offset = end
        if len(packet) < 20:
            raise ValueError("short MoldUDP64 header")
        session = packet[:10]
        seq = struct.unpack_from(">Q", packet, 10)[0]
        count = struct.unpack_from(">H", packet, 18)[0]
        cursor = 20
        messages = []
        if count not in (0, 65535):
            for _ in range(count):
                if cursor + 2 > len(packet):
                    raise ValueError("truncated message length")
                size = struct.unpack_from(">H", packet, cursor)[0]
                cursor += 2
                if cursor + size > len(packet):
                    raise ValueError("truncated message")
                messages.append(packet[cursor:cursor + size])
                cursor += size
        if cursor != len(packet):
            raise ValueError("trailing packet bytes")
        yield session, seq, count, messages

