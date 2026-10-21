"""Permanent unlimited entitlement for one verified Auth0 identity.

Other accounts keep the existing trial and Team project limits. This module
does not add customer-wide quotas.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.account_entitlement import ENTITLEMENT_UNLIMITED, AccountEntitlement
from models.user import PLAN_LITE, PLAN_PRO, User

OWNER_VERIFIED_EMAIL = "john@fotonconsulting.com"
OWNER_UNLIMITED_LABEL = "Owner — Unlimited"
DEV_OWNER_AUTH0_ID = "dev:john@fotonconsulting.com"
SR1_API_AUDIENCE = "https://smartrisk.fotonconsulting.com/api"
SR1_CALLBACK_ORIGINS = (
    "https://fmea-frontend-dczh.onrender.com",
    "https://sr1-sandbox-frontend-dczh.onrender.com",
)


def _env_name() -> str:
    return (os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or os.getenv("ENV") or "development").lower()


def trusted_issuer() -> str:
    """Issuer accepted for the owner grant. Production must set AUTH0_DOMAIN."""
    raw = (os.getenv("AUTH0_DOMAIN") or "").strip()
    if not raw:
        if _env_name() in ("production", "prod", "staging"):
            return ""
        raw = "dev-dsf588bqn08hhddj.us.auth0.com"
    if raw.startswith("https://") or raw.startswith("http://"):
        base = raw.rstrip("/")
    else:
        base = f"https://{raw.strip('/')}"
    return f"{base}/"


def production_auth0_configuration_error() -> Optional[str]:
    """Production and staging must name the Auth0 tenant and the SR1 API."""
    if _env_name() not in ("production", "prod", "staging"):
        return None
    if not (os.getenv("AUTH0_DOMAIN") or "").strip():
        return "AUTH0_DOMAIN is not set"
    audience = (os.getenv("API_AUDIENCE") or os.getenv("AUTH0_AUDIENCE") or "").strip()
    if audience != SR1_API_AUDIENCE:
        return "API_AUDIENCE is not the SmartRisk 1 API identifier"
    return None


def token_algorithm(token: str) -> str:
    try:
        from jose import jwt

        return str(jwt.get_unverified_header(token).get("alg") or "")
    except Exception:
        return ""


@dataclass(frozen=True)
class VerifiedIdentity:
    issuer: Optional[str]
    subject: str
    email: Optional[str]
    email_verified: bool
    algorithm: str

    @staticmethod
    def anonymous() -> "VerifiedIdentity":
        return VerifiedIdentity(None, "", None, False, "")


def identity_from_token(payload: dict, algorithm: str) -> VerifiedIdentity:
    prefix = "https://smartrisk.fotonconsulting.com/"
    email = payload.get(prefix + "email") or payload.get("email")
    verified = payload.get(prefix + "email_verified", payload.get("email_verified")) is True
    return VerifiedIdentity(
        issuer=payload.get("iss") if isinstance(payload.get("iss"), str) else None,
        subject=str(payload.get("sub") or ""),
        email=email if isinstance(email, str) else None,
        email_verified=verified,
        algorithm=algorithm or "",
    )


def is_verified_owner_identity(identity: VerifiedIdentity) -> bool:
    if identity.algorithm != "RS256":
        return False
    issuer = trusted_issuer()
    if not issuer or identity.issuer != issuer:
        return False
    subject = (identity.subject or "").strip()
    if not subject or subject.startswith("dev:"):
        return False
    if not identity.email_verified:
        return False
    return (identity.email or "").strip().lower() == OWNER_VERIFIED_EMAIL


@dataclass(frozen=True)
class EntitlementDecision:
    unlimited: bool
    permanent: bool
    plan: str
    label: Optional[str]
    project_cap: Optional[int]

    def as_api(self) -> dict:
        quotas = {
            "projects": None if self.unlimited else self.project_cap,
            "components": None,
            "fmea_analyses": None,
            "ai_generations": None,
            "reports": None,
            "exports": None,
        }
        return {
            "unlimited": self.unlimited,
            "permanent": self.permanent,
            "label": self.label,
            "quotas": quotas,
        }


def _grant_for_identity(db: Session, identity: VerifiedIdentity):
    if identity.algorithm != "RS256" or not identity.issuer or not identity.subject:
        return None
    if identity.subject.startswith("dev:") or identity.issuer != trusted_issuer():
        return None
    return (
        db.query(AccountEntitlement)
        .filter(
            AccountEntitlement.issuer == identity.issuer,
            AccountEntitlement.subject == identity.subject,
            AccountEntitlement.kind == ENTITLEMENT_UNLIMITED,
            AccountEntitlement.permanent.is_(True),
        )
        .first()
    )


def identity_has_permanent_unlimited(db: Session, identity: VerifiedIdentity) -> bool:
    """Recognize an existing grant by verified issuer and subject, not mutable email."""
    return _grant_for_identity(db, identity) is not None


def maybe_provision_owner_grant(db: Session, identity: VerifiedIdentity) -> None:
    if not is_verified_owner_identity(identity):
        return
    if _grant_for_identity(db, identity) is not None:
        return
    existing = (
        db.query(AccountEntitlement)
        .filter(
            AccountEntitlement.provisioned_email == OWNER_VERIFIED_EMAIL,
            AccountEntitlement.kind == ENTITLEMENT_UNLIMITED,
            AccountEntitlement.permanent.is_(True),
        )
        .first()
    )
    if existing is not None and existing.subject != identity.subject:
        return
    try:
        db.add(
            AccountEntitlement(
                issuer=identity.issuer,
                subject=identity.subject,
                provisioned_email=OWNER_VERIFIED_EMAIL,
                kind=ENTITLEMENT_UNLIMITED,
                permanent=True,
            )
        )
        db.commit()
    except IntegrityError:
        db.rollback()


def user_has_permanent_unlimited(db: Session, user: User) -> bool:
    subject = getattr(user, "auth0_id", None) or ""
    if not subject or subject.startswith("dev:"):
        return False
    issuer = trusted_issuer()
    if not issuer:
        return False
    row = (
        db.query(AccountEntitlement)
        .filter(
            AccountEntitlement.issuer == issuer,
            AccountEntitlement.subject == subject,
            AccountEntitlement.kind == ENTITLEMENT_UNLIMITED,
            AccountEntitlement.permanent.is_(True),
        )
        .first()
    )
    return row is not None


def baseline_project_cap(user: User) -> Optional[int]:
    """Project cap already enforced for trial and Team accounts. None means the baseline has no count cap."""
    if not (getattr(user, "trial_ends_at", None) or getattr(user, "subscription_status", None)):
        return None
    if getattr(user, "subscription_status", None) in ("active", "trialing"):
        return 3
    if (getattr(user, "plan", None) or PLAN_LITE).lower() != PLAN_PRO:
        return 1
    return None


def evaluate_entitlement(db: Session, user: User, identity: VerifiedIdentity) -> EntitlementDecision:
    maybe_provision_owner_grant(db, identity)
    if _grant_for_identity(db, identity) is not None:
        return EntitlementDecision(True, True, PLAN_PRO, OWNER_UNLIMITED_LABEL, None)
    from auth.plan import get_user_plan

    return EntitlementDecision(False, False, get_user_plan(user), None, baseline_project_cap(user))


def attach_entitlement(user: User, decision: EntitlementDecision) -> EntitlementDecision:
    setattr(user, "entitlement_decision", decision)
    return decision
