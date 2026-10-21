"""One-time rebinding of the known dev owner subject to a verified Auth0 subject.

The source row is selected by auth0_id == dev:john@fotonconsulting.com.
A matching email on a different account is not a source and is not merged.
The internal user id, and therefore project ownership, stays the same.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from auth.entitlements import DEV_OWNER_AUTH0_ID, VerifiedIdentity, is_verified_owner_identity
from crud import user as user_crud
from models.account_entitlement import IdentityMigration


@dataclass(frozen=True)
class MigrationResult:
    status: str
    user_id: str | None = None


def _applied(db: Session, user_id: str) -> IdentityMigration | None:
    return (
        db.query(IdentityMigration)
        .filter(IdentityMigration.user_id == user_id, IdentityMigration.status == "applied")
        .order_by(IdentityMigration.created_at.desc())
        .first()
    )


def apply_owner_identity_migration(db: Session, identity: VerifiedIdentity) -> MigrationResult:
    if not is_verified_owner_identity(identity):
        return MigrationResult("rejected")

    source = user_crud.get_user_by_auth0_id(db, DEV_OWNER_AUTH0_ID)
    target = user_crud.get_user_by_auth0_id(db, identity.subject)

    if source is None:
        if target is not None and _applied(db, target.id) and _applied(db, target.id).target_subject == identity.subject:
            return MigrationResult("already_applied", target.id)
        return MigrationResult("not_applicable")

    if target is not None and target.id != source.id:
        db.add(
            IdentityMigration(
                user_id=source.id,
                source_auth0_id=DEV_OWNER_AUTH0_ID,
                target_issuer=identity.issuer or "",
                target_subject=identity.subject,
                status="conflict",
            )
        )
        db.commit()
        return MigrationResult("conflict", source.id)

    source.auth0_id = identity.subject
    db.add(
        IdentityMigration(
            user_id=source.id,
            source_auth0_id=DEV_OWNER_AUTH0_ID,
            target_issuer=identity.issuer or "",
            target_subject=identity.subject,
            status="applied",
        )
    )
    db.commit()
    db.refresh(source)
    return MigrationResult("applied", source.id)


def rollback_owner_identity_migration(db: Session, user_id: str) -> MigrationResult:
    row = _applied(db, user_id)
    if row is None:
        return MigrationResult("nothing_to_roll_back", user_id)
    user = user_crud.get_user_by_id(db, user_id)
    if user is None or user.auth0_id != row.target_subject:
        return MigrationResult("conflict", user_id)
    holder = user_crud.get_user_by_auth0_id(db, DEV_OWNER_AUTH0_ID)
    if holder is not None and holder.id != user.id:
        return MigrationResult("conflict", user_id)
    user.auth0_id = DEV_OWNER_AUTH0_ID
    row.status = "rolled_back"
    row.rolled_back_at = datetime.now(timezone.utc)
    db.commit()
    return MigrationResult("rolled_back", user.id)
