"""
SaaS plan-based feature gating.

Centralized plan checks for Pro-only endpoints.
Compatible with future Stripe subscription integration.
"""
from fastapi import Depends, HTTPException, status
from models.user import User, PLAN_LITE, PLAN_PRO
from auth.dependencies import get_current_user
from datetime import datetime, timezone


def get_user_plan(user: User) -> str:
    """Resolve user's plan. Default to lite if not set."""
    plan = getattr(user, "plan", None) or PLAN_LITE
    if str(plan).lower() == PLAN_PRO and getattr(user, "subscription_status", None) in (None, "active", "trialing"):
        return PLAN_PRO
    end = getattr(user, "trial_ends_at", None)
    if end is not None:
        # SQLite returns naive timestamps; stored trial dates are UTC.
        end_utc = end if end.tzinfo else end.replace(tzinfo=timezone.utc)
        if end_utc > datetime.now(timezone.utc):
            return PLAN_PRO
    return PLAN_LITE


def require_pro(user: User = Depends(get_current_user)) -> User:
    """
    Dependency: require Pro plan. Raises 403 if user has Lite plan.
    Use for Pro-only endpoints.
    """
    plan = get_user_plan(user)
    if plan != PLAN_PRO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires SmartRisk Pro. Upgrade your plan to access projects, traceability, and more.",
        )
    return user


def is_pro(user: User) -> bool:
    """Helper: returns True if user has Pro plan."""
    return get_user_plan(user) == PLAN_PRO


def enforce_trial_project_limit(user: User, existing_count: int) -> None:
    """Limit current trial to one project and a subscribed Team owner to three."""
    if getattr(user, "subscription_status", None) in ("active", "trialing") and existing_count >= 3:
        raise HTTPException(status_code=403, detail="The Team plan includes three projects.")
    if (getattr(user, "plan", None) or PLAN_LITE).lower() != PLAN_PRO and existing_count >= 1:
        raise HTTPException(status_code=403, detail="The 14-day trial includes one project. Upgrade to create more.")
