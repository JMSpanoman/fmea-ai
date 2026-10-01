"""Owner-managed Team seats, identity-bound invitations, and workspace scope."""
from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from models.user import User, TeamInvitation

MAX_TEAM_SEATS = 5


def utcnow():
    return datetime.now(timezone.utc)


def as_utc(value):
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def workspace_owner_id(db: Session, user_id: str) -> str:
    user = db.get(User, user_id)
    return (user.team_owner_id or user.id) if user else user_id


def lock_owner(db: Session, owner_id: str) -> User:
    # The no-op UPDATE acquires a write lock on SQLite as well as PostgreSQL.
    # It serializes seat/project reservations until the caller commits.
    db.execute(update(User).where(User.id == owner_id).values(id=owner_id))
    owner = db.get(User, owner_id)
    if owner is None:
        raise HTTPException(404, "Team not found")
    return owner


def require_team_owner(user: User):
    if user.team_owner_id or not user.auth0_id or user.auth0_id.startswith("dev:"):
        raise HTTPException(403, "Only the billing owner can manage this team")
    if user.plan != "pro" or user.subscription_status != "active":
        raise HTTPException(403, "An active Team subscription is required")


def pending_invitations(db: Session, owner_id: str):
    return db.query(TeamInvitation).filter(
        TeamInvitation.owner_id == owner_id,
        TeamInvitation.accepted_at.is_(None), TeamInvitation.revoked_at.is_(None),
        TeamInvitation.expires_at > utcnow(),
    )


def invite(db: Session, owner: User, email: str):
    require_team_owner(owner)
    email = email.strip().lower()
    if not email or "@" not in email or len(email) > 254:
        raise HTTPException(422, "Enter a valid email address")
    owner = lock_owner(db, owner.id)
    members = db.query(User).filter(User.team_owner_id == owner.id)
    pending = pending_invitations(db, owner.id)
    if email == owner.email.lower() or members.filter(User.email == email).first() or pending.filter(TeamInvitation.email == email).first():
        raise HTTPException(409, "This email already has a seat or invitation")
    if 1 + members.count() + pending.count() >= MAX_TEAM_SEATS:
        raise HTTPException(409, "The Team plan includes five users, including you and pending invitations")
    token = secrets.token_urlsafe(32)
    invitation = TeamInvitation(owner_id=owner.id, email=email,
        token_hash=hashlib.sha256(token.encode()).hexdigest(), expires_at=utcnow() + timedelta(days=7))
    db.add(invitation)
    db.commit()
    return invitation, token


def accept(db: Session, user: User, token: str):
    if not getattr(user, "is_verified", False) or not user.auth0_id or user.auth0_id.startswith("dev:"):
        raise HTTPException(403, "Verify your email address before accepting this invitation")
    invitation = db.query(TeamInvitation).filter(TeamInvitation.token_hash == hashlib.sha256(token.encode()).hexdigest()).first()
    if invitation is None:
        raise HTTPException(404, "Invitation not found")
    owner = lock_owner(db, invitation.owner_id)
    lock_owner(db, user.id)
    db.refresh(user)
    db.refresh(invitation)
    require_team_owner(owner)
    if invitation.accepted_at or invitation.revoked_at or as_utc(invitation.expires_at) <= utcnow():
        raise HTTPException(410, "This invitation has expired or was already used")
    if user.email.lower() != invitation.email:
        raise HTTPException(403, "Sign in with the email address that was invited")
    if user.id == owner.id or user.team_owner_id or user.stripe_subscription_id:
        raise HTTPException(409, "This account already belongs to a team or has its own subscription")
    if db.query(User).filter(User.team_owner_id == user.id).count():
        raise HTTPException(409, "A team owner cannot join another team")
    if db.query(User).filter(User.team_owner_id == owner.id).count() >= MAX_TEAM_SEATS - 1:
        raise HTTPException(409, "This team is full")
    user.team_owner_id = owner.id
    invitation.accepted_at = utcnow()
    db.commit()
    return owner.id


def remove_member(db: Session, owner: User, member_id: str):
    # The owner must be able to remove members even after cancellation.
    if owner.team_owner_id or member_id == owner.id:
        raise HTTPException(403, "Only the billing owner can remove other members")
    lock_owner(db, owner.id)
    member = db.query(User).filter(User.id == member_id, User.team_owner_id == owner.id).first()
    if member is None:
        raise HTTPException(404, "Member not found")
    member.team_owner_id = None
    db.commit()
