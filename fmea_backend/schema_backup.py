"""Verified SQLite snapshots before schema changes in hosted environments."""
from datetime import datetime, timezone
from contextlib import closing
import hashlib
import logging
import os
from pathlib import Path
import sqlite3
import tempfile
import time

logger = logging.getLogger(__name__)


def backup_before_schema_change(engine):
    environment = (os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or "development").lower()
    if environment not in ("production", "prod", "staging") or engine.dialect.name != "sqlite":
        return None
    database = engine.url.database
    if not database or database == ":memory:":
        return None
    source = Path(database).resolve()
    if not source.exists() or source.stat().st_size == 0:
        return None

    directory = source.parent / "backups"
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    # A content-addressed destination reuses identical backups across restarts.
    # Existing backups are never replaced or automatically deleted.
    fd, temporary = tempfile.mkstemp(prefix=".schema-", suffix=".sqlite3", dir=directory)
    os.close(fd)
    temporary = Path(temporary)
    deadline = time.monotonic() + 60

    def progress(_status, _remaining, _total):
        if time.monotonic() > deadline:
            raise TimeoutError("SQLite backup exceeded 60 seconds; migration stopped")

    try:
        with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True, timeout=10)) as src:
            with closing(sqlite3.connect(temporary)) as dst:
                src.backup(dst, pages=256, progress=progress, sleep=0.05)
                if dst.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                    raise RuntimeError("SQLite backup integrity check failed; migration stopped")
        digest = hashlib.sha256()
        with temporary.open("rb") as data:
            for chunk in iter(lambda: data.read(1024 * 1024), b""):
                digest.update(chunk)
        destination = directory / f"pre-schema-{digest.hexdigest()}.sqlite3"
        if destination.exists():
            # Verify the retained artifact before reusing it.
            with destination.open("rb") as data:
                existing = hashlib.file_digest(data, "sha256").hexdigest()
            if existing != digest.hexdigest():
                raise RuntimeError("Existing SQLite backup does not match its checksum")
        else:
            with temporary.open("rb") as data:
                os.fsync(data.fileno())
            temporary.rename(destination)
            directory_fd = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        logger.info("Pre-schema SQLite backup verified: %s (%s bytes; %s)",
                    destination, destination.stat().st_size, datetime.now(timezone.utc).isoformat())
        return destination
    finally:
        temporary.unlink(missing_ok=True)
