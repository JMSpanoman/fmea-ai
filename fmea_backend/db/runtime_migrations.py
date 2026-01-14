from sqlalchemy import text
from sqlalchemy.engine import Engine, Connection


def _has_column_sqlite(conn: Connection, table: str, column: str) -> bool:
    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
    return any(r[1] == column for r in rows)


def ensure_component_columns(engine: Engine) -> None:
    """
    SQLite-friendly runtime migration:
    SQLAlchemy's create_all does not add missing columns on existing tables.
    We add new Component columns required by the Project Setup Wizard.
    """
    dialect = engine.dialect.name
    if dialect != "sqlite":
        # For Postgres, we expect schema migrations (or manual) in production.
        return

    # Use a single transaction/connection for migration statements
    with engine.begin() as conn:
        # parent_id
        if not _has_column_sqlite(conn, "components", "parent_id"):
            conn.execute(text("ALTER TABLE components ADD COLUMN parent_id VARCHAR"))

        # tags (JSON -> TEXT on SQLite)
        if not _has_column_sqlite(conn, "components", "tags"):
            conn.execute(text("ALTER TABLE components ADD COLUMN tags TEXT"))

        # updated_at
        if not _has_column_sqlite(conn, "components", "updated_at"):
            conn.execute(text("ALTER TABLE components ADD COLUMN updated_at DATETIME"))

