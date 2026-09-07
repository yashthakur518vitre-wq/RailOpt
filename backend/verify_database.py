from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent / "railblock.db"
EXPECTED = ["assets", "blocks", "corridors", "defects", "maintenance_tasks", "plans", "resources", "trains"]

with sqlite3.connect(DB_PATH) as conn:
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    missing = [t for t in EXPECTED if t not in tables]
    print(f"Database: {DB_PATH}")
    print(f"Exists: {DB_PATH.exists()}")
    if missing:
        raise SystemExit(f"Missing tables: {missing}")
    for table in EXPECTED:
        count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        print(f"{table:20} {count:>5}")
    print("Database verification: OK")
