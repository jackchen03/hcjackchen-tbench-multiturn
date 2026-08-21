#!/usr/bin/env python3
import base64,json,subprocess
from pathlib import Path
Path('/app/samples').mkdir(parents=True,exist_ok=True)
samples=[[b'alpha',b'beta\xaa\x55z'],[bytes(range(11))],[b'plain\xaaQ',b'last'],[b'',b'xyz'],[b'0123456789abcdefg']]
for index,records in enumerate(samples):
 payload={'records':[base64.b64encode(value).decode() for value in records]}; source=Path(f'/app/samples/input{index}.json'); source.write_text(json.dumps(payload)+'\n'); result=subprocess.run(['/verifier/legacy_framer'],input=source.read_bytes(),stdout=subprocess.PIPE,check=True); Path(f'/app/samples/output{index}.bin').write_bytes(result.stdout)
edge=[[b'A\xaa\x00U',b'tail'],[b'\xaa\x00\x55',b'other'],[b'x\xaa\x00y\xaa\x55z']]
Path('/app/EDGE_PAYLOADS.json').write_text(json.dumps({'batches':[{'records':[base64.b64encode(v).decode() for v in batch]} for batch in edge]},indent=2)+'\n')
# MAGIC plus fourteen payload bytes produces an exact 16-byte logical stream.
boundary=[[b'12345678901234'],[b'aaaaaa',b'bbbbbb'],[bytes(range(14))]]
Path('/app/BOUNDARY_CASES.json').write_text(json.dumps({'batches':[{'records':[base64.b64encode(v).decode() for v in batch]} for batch in boundary],'expected_tail_hex':'111f00'},indent=2)+'\n')
Path('/app/PROFILING.md').write_text('# Boundary scan profiling\n\nExact 16-byte boundaries still require an empty final block: Fletcher init bytes `0x11 0x1F` and LEB128 `0x00`. Conditional escaping remains limited to `0xAA` followed by `0x55` or `0x00`.\n')
