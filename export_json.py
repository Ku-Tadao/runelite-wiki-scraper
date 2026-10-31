"""Writes every table of data.sqlite to a gzipped JSON file for the plugin.

Usage: python export_json.py output/data.sqlite output/data.json.gz

The format is {"TABLE": {"columns": [...], "rows": [[...], ...]}}, rows in ID order.
The gzip header carries no timestamp, so unchanged data keeps the same checksum.
"""
import gzip
import json
import sqlite3
import sys


def export(db_path, out_path):
    db = sqlite3.connect(db_path)
    tables = {}
    for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"):
        cursor = db.execute(f"SELECT * FROM {name} ORDER BY ID")
        tables[name] = {
            "columns": [c[0] for c in cursor.description],
            "rows": cursor.fetchall(),
        }
    data = json.dumps(tables, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    with open(out_path, "wb") as f, gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as gz:
        gz.write(data)
    return tables


if __name__ == "__main__":
    tables = export(sys.argv[1], sys.argv[2])
    for name, table in tables.items():
        print(name, len(table["rows"]))
