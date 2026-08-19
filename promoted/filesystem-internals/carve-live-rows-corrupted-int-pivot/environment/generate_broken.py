import sqlite3,json,zlib
from pathlib import Path
p=Path('/app/broken.sqlite'); db=Path('/tmp/live.sqlite'); con=sqlite3.connect(db); con.execute('create table T(id INTEGER PRIMARY KEY, name TEXT, val INTEGER)')
rows=[(1,'alpha',11),(2,'bravo',-7),(7,'café',300),(19,'zero',0),(44,'tail',9999)]; con.executemany('insert into T values(?,?,?)',rows); con.commit(); con.close()
data=bytearray(db.read_bytes()); data[:16]=b'BROKEN-SQLITE!!!'; payload=zlib.compress(json.dumps(rows,separators=(',',':'),ensure_ascii=False).encode())
p.write_bytes(data+b'\nGHOST:[999,"decoy",123]\n'+b'CARVE-LIVE-ROWS-V1\n'+payload); db.unlink()
