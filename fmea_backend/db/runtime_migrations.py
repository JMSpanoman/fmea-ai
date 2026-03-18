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


def ensure_user_columns(engine: Engine) -> None:
    """
    SQLite-friendly runtime migration for auth:
    Older demo DB initializers created a `users` table without `auth0_id` and `created_at`.
    The running app expects these columns for /auth/me and token->user resolution.
    """
    dialect = engine.dialect.name
    if dialect != "sqlite":
        return

    with engine.begin() as conn:
        if not _has_column_sqlite(conn, "users", "auth0_id"):
            conn.execute(text("ALTER TABLE users ADD COLUMN auth0_id VARCHAR"))

        if not _has_column_sqlite(conn, "users", "created_at"):
            conn.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME"))

        # SaaS plan tier: lite | pro (default lite for new users)
        if not _has_column_sqlite(conn, "users", "plan"):
            conn.execute(text("ALTER TABLE users ADD COLUMN plan VARCHAR DEFAULT 'lite'"))


def ensure_library_reference_columns(engine: Engine) -> None:
    """
    Add Risk Knowledge Base library reference columns to fmea_rows and risk_item_versions
    so FMEA and risk records can link to hazard, harm, risk_control, and verification libraries.
    """
    dialect = engine.dialect.name
    if dialect != "sqlite":
        return

    lib_cols = [
        "hazard_library_id",
        "harm_library_id",
        "risk_control_library_id",
        "verification_library_id",
    ]
    with engine.begin() as conn:
        for col in lib_cols:
            if not _has_column_sqlite(conn, "fmea_rows", col):
                conn.execute(text(f"ALTER TABLE fmea_rows ADD COLUMN {col} VARCHAR"))
            if not _has_column_sqlite(conn, "risk_item_versions", col):
                conn.execute(text(f"ALTER TABLE risk_item_versions ADD COLUMN {col} VARCHAR"))


def ensure_hazard_generation_rule_columns(engine: Engine) -> None:
    """Add optional library and template columns to hazard_generation_rules."""
    dialect = engine.dialect.name
    if dialect != "sqlite":
        return
    with engine.begin() as conn:
        for col in [
            "harm_library_id",
            "risk_control_library_id",
            "verification_library_id",
            "failure_mode_template",
            "hazardous_situation_template",
        ]:
            if not _has_column_sqlite(conn, "hazard_generation_rules", col):
                typ = "VARCHAR" if col != "failure_mode_template" and col != "hazardous_situation_template" else "TEXT"
                conn.execute(text(f"ALTER TABLE hazard_generation_rules ADD COLUMN {col} {typ}"))


def ensure_suggestion_set_project_id(engine: Engine) -> None:
    """Add project_id to risk_analysis_suggestion_sets for component-scoped suggestions."""
    dialect = engine.dialect.name
    if dialect != "sqlite":
        return
    with engine.begin() as conn:
        if not _has_column_sqlite(conn, "risk_analysis_suggestion_sets", "project_id"):
            conn.execute(text("ALTER TABLE risk_analysis_suggestion_sets ADD COLUMN project_id VARCHAR"))


def ensure_hazard_library_columns(engine: Engine) -> None:
    """
    Align hazard_library with schema: hazard_id, hazard_name, typical_*, etc.
    Renames code->hazard_id, name->hazard_name (SQLite 3.25+) and adds new columns if missing.
    """
    dialect = engine.dialect.name
    if dialect != "sqlite":
        return
    with engine.begin() as conn:
        table = "hazard_library"
        if _has_column_sqlite(conn, table, "code") and not _has_column_sqlite(conn, table, "hazard_id"):
            conn.execute(text("ALTER TABLE hazard_library RENAME COLUMN code TO hazard_id"))
        if _has_column_sqlite(conn, table, "name") and not _has_column_sqlite(conn, table, "hazard_name"):
            conn.execute(text("ALTER TABLE hazard_library RENAME COLUMN name TO hazard_name"))
        for col, col_type in [
            ("typical_hazardous_situation", "TEXT"),
            ("typical_harms", "TEXT"),
            ("example_controls", "TEXT"),
            ("verification_examples", "TEXT"),
            ("lifecycle_phase", "VARCHAR(128)"),
        ]:
            if not _has_column_sqlite(conn, table, col):
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
