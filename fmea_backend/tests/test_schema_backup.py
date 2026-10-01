import sqlite3

import pytest
from sqlalchemy import create_engine

from schema_backup import backup_before_schema_change


def test_snapshot_preserves_existing_data_before_migration_and_reuses_identical_copy(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    path = tmp_path / "customer.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE projects (id INTEGER, title TEXT)")
        conn.execute("INSERT INTO projects VALUES (1, 'Saved FMEA')")
    engine = create_engine(f"sqlite:///{path}")
    snapshot = backup_before_schema_change(engine)
    assert snapshot == backup_before_schema_change(engine)
    with sqlite3.connect(path) as conn:
        conn.execute("ALTER TABLE projects ADD COLUMN migrated TEXT")
    with sqlite3.connect(snapshot) as conn:
        assert conn.execute("SELECT * FROM projects").fetchall() == [(1, "Saved FMEA")]
        assert conn.execute("PRAGMA integrity_check").fetchone() == ("ok",)
    assert snapshot.stat().st_mode & 0o077 == 0
    engine.dispose()


def test_corrupt_database_stops_migration_backup(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    path = tmp_path / "corrupt.db"
    path.write_bytes(b"not a SQLite database")
    engine = create_engine(f"sqlite:///{path}")
    with pytest.raises(sqlite3.DatabaseError):
        backup_before_schema_change(engine)
    assert list((tmp_path / "backups").iterdir()) == []
    engine.dispose()
