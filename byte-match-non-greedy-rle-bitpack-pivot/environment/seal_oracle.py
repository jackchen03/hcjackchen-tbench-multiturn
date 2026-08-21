from pathlib import Path

data = Path("/src/oracle.py").read_bytes()
enc = bytes(byte ^ 0xA7 for byte in data)
rows = []
for start in range(0, len(enc), 20):
    rows.append(",".join(str(x) for x in enc[start:start + 20]))
Path("/out/oracle_payload.h").write_text(
    "static const unsigned char payload[] = {\n" + ",\n".join(rows) + "\n};\n"
    "static const unsigned long payload_len = sizeof(payload);\n"
)
