"""
SaaS plan-based feature gating.

Centralized plan checks for Pro-only endpoints.
Compatible with future Stripe subscription integration.
"""
from fastapi import Depends, HTTPException, status
from models.user import User, PLAN_LITE, PLAN_PRO
from auth.dependencies import get_current_user


def get_user_plan(user: User) -> str:
    """Resolve user's plan. Default to lite if not set."""
    plan = getattr(user, "plan", None) or PLAN_LITE
    return str(plan).lower() if plan else PLAN_LITE


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
