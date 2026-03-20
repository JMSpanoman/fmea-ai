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


def ensure_risk_acceptability_columns(engine: Engine) -> None:
    """
    SQLite-friendly runtime migration for newly added RAC columns.
    Prevents 500s when model evolves before manual SQL migrations are applied.
    """
    dialect = engine.dialect.name
    if dialect != "sqlite":
        return
    with engine.begin() as conn:
        table = "risk_acceptability_criteria"
        for col, col_type in [
            ("section_metadata", "TEXT"),
            ("readiness_metrics", "TEXT"),
            ("review_comments", "TEXT"),
            ("approval_notes", "TEXT"),
            ("rejection_reason", "TEXT"),
            ("supersedes_id", "VARCHAR"),
            ("sections_json", "TEXT"),
            ("section_document_version", "INTEGER DEFAULT 1"),
        ]:
            if not _has_column_sqlite(conn, table, col):
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))


def ensure_hazard_analysis_item_columns(engine: Engine) -> None:
    """
    SQLite-friendly runtime migration for hazard_analysis_items regulatory extensions.
    """
    dialect = engine.dialect.name
    if dialect != "sqlite":
        return
    with engine.begin() as conn:
        table = "hazard_analysis_items"
        for col, col_type in [
            ("sequence_of_events", "TEXT"),
            ("initial_occurrence", "INTEGER"),
            ("risk_controls", "TEXT"),
            ("residual_occurrence", "INTEGER"),
            ("risk_acceptability_decision", "VARCHAR(100)"),
            ("risk_acceptability_justification", "TEXT"),
            ("capa_reference", "TEXT"),
            ("approver_role", "VARCHAR(255)"),
            ("approval_meaning", "TEXT"),
            ("version_lock", "BOOLEAN DEFAULT 0"),
            ("review_date", "DATETIME"),
            ("review_frequency", "VARCHAR(255)"),
            ("last_reviewed_by", "VARCHAR"),
            ("post_market_trigger", "BOOLEAN DEFAULT 0"),
            ("benefit_risk_analysis_required", "BOOLEAN DEFAULT 0"),
            ("benefit_risk_justification", "TEXT"),
        ]:
            if not _has_column_sqlite(conn, table, col):
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))

        table = "organization_risk_criteria_configs"
        for col, col_type in [
            ("organization_id", "VARCHAR"),
            ("template_name", "VARCHAR"),
            ("severity_rationale", "TEXT"),
            ("probability_rationale", "TEXT"),
            ("matrix_rationale", "TEXT"),
            ("decision_rules_rationale", "TEXT"),
            ("overall_residual_risk_methods", "TEXT"),
            ("approval_policy", "TEXT"),
            ("is_approved", "BOOLEAN DEFAULT 0"),
            ("approved_by", "VARCHAR"),
            ("approved_at", "DATETIME"),
        ]:
            if not _has_column_sqlite(conn, table, col):
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))

        table = "project_risk_criteria_overrides"
        for col, col_type in [
            ("terminology_overrides", "TEXT"),
            ("severity_rationale", "TEXT"),
            ("probability_rationale", "TEXT"),
            ("matrix_rationale", "TEXT"),
            ("decision_rules_rationale", "TEXT"),
            ("overall_residual_risk_methods", "TEXT"),
            ("workflow_state", "VARCHAR DEFAULT 'draft'"),
            ("approval_notes", "TEXT"),
            ("rejection_reason", "TEXT"),
        ]:
            if not _has_column_sqlite(conn, table, col):
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))


def ensure_fmea_rule_engine_columns(engine: Engine) -> None:
    """
    FMEA row extensions for deterministic risk acceptability rule engine + audit support.
    """
    dialect = engine.dialect.name
    if dialect != "sqlite":
        return
    with engine.begin() as conn:
        table = "fmea_rows"
        for col, col_type in [
            ("device_function", "TEXT"),
            ("hazard", "TEXT"),
            ("harm", "TEXT"),
            ("action_taken", "TEXT"),
            ("initial_risk_classification", "VARCHAR(32)"),
            ("residual_risk_classification", "VARCHAR(32)"),
            ("benefit_risk_required", "BOOLEAN DEFAULT 0"),
            ("reviewer_justification", "TEXT"),
            ("reviewer_name", "VARCHAR(255)"),
            ("reviewer_date", "DATETIME"),
            ("critical_function_flag", "BOOLEAN DEFAULT 0"),
            ("approval_blocked", "BOOLEAN DEFAULT 0"),
            ("rule_engine_result_json", "TEXT"),
            ("ai_suggested_values_json", "TEXT"),
            ("risk_criteria_version_applied", "INTEGER"),
            ("acceptable_for_release", "BOOLEAN DEFAULT 1"),
            ("benefit_risk_formal_approval_recorded", "BOOLEAN DEFAULT 0"),
            ("bra_clinical_benefit_documented", "BOOLEAN DEFAULT 0"),
            ("bra_benefit_vs_residual_risk_documented", "BOOLEAN DEFAULT 0"),
            ("bra_state_of_the_art_documented", "BOOLEAN DEFAULT 0"),
            ("bra_supporting_evidence_addressed", "BOOLEAN DEFAULT 0"),
            ("bra_approval_clinical_medical_recorded", "BOOLEAN DEFAULT 0"),
            ("bra_approval_quality_regulatory_recorded", "BOOLEAN DEFAULT 0"),
            ("bra_approval_design_authority_recorded", "BOOLEAN DEFAULT 0"),
            ("cross_functional_review_completed", "BOOLEAN DEFAULT 0"),
            ("formal_release_approval_recorded", "BOOLEAN DEFAULT 0"),
            ("additional_controls_reduced_risk", "BOOLEAN DEFAULT 0"),
            ("benefit_risk_analysis_approved", "BOOLEAN DEFAULT 0"),
            ("critical_hazard_severity_floor_waived", "BOOLEAN DEFAULT 0"),
            ("risk_eliminated", "BOOLEAN DEFAULT 0"),
            ("system_level_verification_recorded", "BOOLEAN DEFAULT 0"),
            ("critical_hazard_category_flag", "BOOLEAN DEFAULT 0"),
            ("system_level_verification_required", "BOOLEAN DEFAULT 0"),
            ("residual_all_feasible_controls_implemented", "BOOLEAN DEFAULT 0"),
            ("residual_further_reduction_not_practicable", "BOOLEAN DEFAULT 0"),
        ]:
            if not _has_column_sqlite(conn, table, col):
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))


def ensure_project_profile_governance_columns(engine: Engine) -> None:
    """Project-level RMF/RMR attestations on project_profiles (SQLite runtime migration)."""
    dialect = engine.dialect.name
    if dialect != "sqlite":
        return
    with engine.begin() as conn:
        table = "project_profiles"
        for col, col_type in [
            ("overall_device_benefit_risk_profile_acceptable", "BOOLEAN"),
            ("rmr_overall_residual_risk_conclusion_documented", "BOOLEAN"),
        ]:
            if not _has_column_sqlite(conn, table, col):
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
