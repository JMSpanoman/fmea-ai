from sqlalchemy.orm import Session
from models.generated_artifact import GeneratedArtifact
from typing import Optional
import uuid
from datetime import datetime, timezone
from pathlib import Path


def create_generated_artifact(
    db: Session,
    *,
    user_id: str,
    filename: str,
    artifact_type: str,
    project_id: Optional[str] = None,
    expires_at=None,
) -> GeneratedArtifact:
    """
    Create a GeneratedArtifact record.
    Note: We intentionally keep this minimal (no schemas) for low-friction adoption.
    """
    rec = GeneratedArtifact(
        id=str(uuid.uuid4()),
        user_id=user_id,
        project_id=project_id,
        filename=filename,
        artifact_type=artifact_type,
        expires_at=expires_at,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def get_generated_artifact_for_user(
    db: Session,
    *,
    user_id: str,
    filename: str,
    artifact_type: str,
) -> Optional[GeneratedArtifact]:
    return (
        db.query(GeneratedArtifact)
        .filter(
            GeneratedArtifact.user_id == user_id,
            GeneratedArtifact.filename == filename,
            GeneratedArtifact.artifact_type == artifact_type,
        )
        .order_by(GeneratedArtifact.created_at.desc())
        .first()
    )


def delete_generated_artifact_for_user(
    db: Session,
    *,
    user_id: str,
    filename: str,
    artifact_type: str,
) -> bool:
    rec = get_generated_artifact_for_user(
        db, user_id=user_id, filename=filename, artifact_type=artifact_type
    )
    if not rec:
        return False
    db.delete(rec)
    db.commit()
    return True


def _safe_path_in_dir(base_dir: Path, filename: str) -> Path:
    """
    Resolve filename within base_dir and ensure it cannot escape the directory.
    This is defense-in-depth; filenames are already validated at the router layer.
    """
    if not isinstance(filename, str) or not filename or "/" in filename or "\\" in filename:
        raise ValueError("Invalid filename")
    base = base_dir.resolve()
    candidate = (base / filename).resolve()
    if candidate.parent != base:
        raise ValueError("Invalid filename path")
    try:
        if not candidate.is_relative_to(base):
            raise ValueError("Invalid filename path")
    except AttributeError:
        if str(candidate).find(str(base)) != 0:
            raise ValueError("Invalid filename path")
    return candidate


def cleanup_generated_artifacts(
    db: Session,
    *,
    base_dirs: Optional[dict[str, Path]] = None,
    now: Optional[datetime] = None,
) -> dict:
    """
    Cleanup routine:
    - deletes expired GeneratedArtifact rows
    - deletes expired files from disk (best-effort)
    - removes DB rows for files that no longer exist

    Returns counts for logging/observability.
    """
    if base_dirs is None:
        base_dirs = {
            "word_report": Path("temp"),
            "template": Path("templates"),
        }
    if now is None:
        now = datetime.now(timezone.utc)

    deleted_rows_expired = 0
    deleted_files_expired = 0
    deleted_rows_missing_file = 0

    # 1) Expired artifacts: delete file + row
    expired = (
        db.query(GeneratedArtifact)
        .filter(GeneratedArtifact.expires_at.isnot(None))
        .filter(GeneratedArtifact.expires_at <= now)
        .all()
    )

    for rec in expired:
        base = base_dirs.get(rec.artifact_type)
        if base:
            try:
                file_path = _safe_path_in_dir(base, rec.filename)
                if file_path.exists() and file_path.is_file():
                    file_path.unlink()
                    deleted_files_expired += 1
            except Exception:
                # Best-effort file deletion; still remove DB row
                pass
        try:
            db.delete(rec)
            deleted_rows_expired += 1
        except Exception:
            # continue; we'll try to commit what we can
            pass

    db.commit()

    # 2) Orphaned DB rows: if expected file is missing, remove the row
    all_recs = db.query(GeneratedArtifact).all()
    for rec in all_recs:
        base = base_dirs.get(rec.artifact_type)
        if not base:
            continue
        try:
            file_path = _safe_path_in_dir(base, rec.filename)
            if not file_path.exists():
                db.delete(rec)
                deleted_rows_missing_file += 1
        except Exception:
            # If path resolution fails, fail closed and remove row
            try:
                db.delete(rec)
                deleted_rows_missing_file += 1
            except Exception:
                pass

    db.commit()

    return {
        "deleted_rows_expired": deleted_rows_expired,
        "deleted_files_expired": deleted_files_expired,
        "deleted_rows_missing_file": deleted_rows_missing_file,
    }

