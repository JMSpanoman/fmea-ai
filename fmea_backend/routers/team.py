from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User, TeamInvitation
from business_logic import team_access

router = APIRouter(prefix="/team", tags=["Team"])


class InviteRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)


class AcceptRequest(BaseModel):
    token: str = Field(min_length=20, max_length=200)


@router.get("")
def current_team(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_id = user.team_owner_id or user.id
    owner = db.get(User, owner_id)
    members = db.query(User).filter(User.team_owner_id == owner_id).all()
    pending = team_access.pending_invitations(db, owner_id).all() if owner_id == user.id else []
    return {"owner_id": owner_id, "is_owner": owner_id == user.id, "seat_limit": 5,
            "members": [{"id": m.id, "email": m.email, "is_owner": m.id == owner_id} for m in [owner, *members] if m],
            "invitations": [{"id": i.id, "email": i.email, "expires_at": i.expires_at} for i in pending]}


@router.post("/invitations", status_code=201)
def create_invitation(data: InviteRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invitation, token = team_access.invite(db, user, data.email)
    # The owner copies the invitation link; no email is sent without an email service.
    return {"id": invitation.id, "token": token, "email": invitation.email, "expires_at": invitation.expires_at}


@router.post("/accept")
def accept_invitation(data: AcceptRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"owner_id": team_access.accept(db, user, data.token)}


@router.delete("/invitations/{invitation_id}", status_code=204)
def revoke_invitation(invitation_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.team_owner_id:
        raise HTTPException(403, "Only the billing owner can revoke invitations")
    team_access.lock_owner(db, user.id)
    invitation = db.query(TeamInvitation).filter(TeamInvitation.id == invitation_id, TeamInvitation.owner_id == user.id).first()
    if invitation is None:
        raise HTTPException(404, "Invitation not found")
    invitation.revoked_at = team_access.utcnow()
    db.commit()


@router.delete("/members/{member_id}", status_code=204)
def remove_team_member(member_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team_access.remove_member(db, user, member_id)
