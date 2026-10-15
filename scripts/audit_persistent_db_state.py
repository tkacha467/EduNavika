import sqlite3
import hashlib
import json
import os

db_path = r"D:\EduNavika\edunavika.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} does not exist")
    exit(1)

with open(db_path, "rb") as f:
    file_bytes = f.read()
sha256 = hashlib.sha256(file_bytes).hexdigest()
size = len(file_bytes)

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("PRAGMA integrity_check")
integrity = c.fetchall()

c.execute("PRAGMA foreign_key_check")
fk_check = c.fetchall()

c.execute("SELECT version_num FROM alembic_version")
alembic_rev = [r[0] for r in c.fetchall()]

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
tables = [r[0] for r in c.fetchall()]

counts = {}
for t in tables:
    c.execute(f'SELECT count(*) FROM "{t}"')
    counts[t] = c.fetchone()[0]

conn.close()

result = {
    "db_path": db_path,
    "sha256": sha256,
    "size_bytes": size,
    "integrity": integrity,
    "foreign_key_check": fk_check,
    "alembic_version": alembic_rev,
    "table_count": len(tables),
    "row_counts": counts
}

print(json.dumps(result, indent=2))
