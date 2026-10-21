from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.sql import func

from database import Base
import uuid

ENTITLEMENT_UNLIMITED = "unlimited"


class AccountEntitlement(Base):
    """Permanent grant bound to an Auth0 issuer and subject.

    Billing webhooks do not write this table. The provisioned email is the
    verified address seen when the grant was created; later requests authorize
    from the issuer and subject.
    """

    __tablename__ = "account_entitlements"
    __table_args__ = (
        UniqueConstraint("issuer", "subject", "kind", name="uq_account_entitlement_identity"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    issuer = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False, index=True)
    provisioned_email = Column(String, nullable=False)
    kind = Column(String, nullable=False, default=ENTITLEMENT_UNLIMITED)
    permanent = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class IdentityMigration(Base):
    """Audit record for the one-time dev-owner subject rebinding."""

    __tablename__ = "identity_migrations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    source_auth0_id = Column(String, nullable=False)
    target_issuer = Column(String, nullable=False)
    target_subject = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    rolled_back_at = Column(DateTime(timezone=True), nullable=True)
