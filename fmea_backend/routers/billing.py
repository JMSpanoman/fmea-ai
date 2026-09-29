"""Stripe subscription operations. Public activation requires verified Auth0 sign-in."""
import os
import secrets
import string

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from auth.dependencies import get_current_user
from auth.plan import get_user_plan
from database import get_db
from models.user import BillingEvent, PLAN_LITE, PLAN_PRO, User
from business_logic.team_access import lock_owner

router = APIRouter()


def _data(value):
    # stripe-python 15 resources are no longer dict subclasses.
    return value.to_dict() if hasattr(value, "to_dict") else value


def _configured(*, webhook=False):
    if os.getenv("ENABLE_SR1_BILLING", "false").lower() != "true":
        raise HTTPException(503, "Billing is not available")
    key = os.getenv("STRIPE_RESTRICTED_KEY") or os.getenv("STRIPE_SECRET_KEY")
    if not key or (webhook and not os.getenv("STRIPE_WEBHOOK_SECRET")):
        raise HTTPException(503, "Billing is not configured")
    is_live = key.startswith(("sk_live_", "rk_live_"))
    is_test = key.startswith(("sk_test_", "rk_test_"))
    if not (is_live or is_test) or is_live != (os.getenv("ENABLE_LIVE_BILLING", "false").lower() == "true"):
        raise HTTPException(503, "Stripe key mode does not match the billing environment")
    import stripe
    return stripe, stripe.StripeClient(key, max_network_retries=2)


def _price(client, interval: str) -> str:
    if interval not in ("monthly", "yearly"):
        raise HTTPException(422, "Choose monthly or yearly")
    price_id = os.getenv("STRIPE_PRICE_MONTHLY" if interval == "monthly" else "STRIPE_PRICE_YEARLY")
    if not price_id:
        raise HTTPException(503, "Billing price is not configured")
    price = client.v1.prices.retrieve(price_id)
    expected_amount = 39900 if interval == "monthly" else 399000
    expected_interval = "month" if interval == "monthly" else "year"
    if (not price.active or price.currency != "eur" or price.unit_amount != expected_amount
            or price.tax_behavior != "exclusive"
            or not price.recurring or price.recurring.interval != expected_interval
            or price.recurring.interval_count != 1):
        raise HTTPException(503, "The configured EUR price does not match the published plan")
    return price_id


def _customer_user(user: User):
    if not user.auth0_id or user.auth0_id.startswith("dev:"):
        raise HTTPException(403, "Verified customer sign-in required")
    if user.team_owner_id:
        raise HTTPException(403, "The team owner manages this subscription")


def _paid_status(subscription) -> bool:
    subscription = _data(subscription)
    prices = {os.getenv("STRIPE_PRICE_MONTHLY"), os.getenv("STRIPE_PRICE_YEARLY")}
    prices.discard(None)
    items = subscription["items"]["data"]
    return (
        subscription["status"] == "active"
        and len(items) == 1
        and items[0]["price"]["id"] in prices
        and items[0]["quantity"] == 1
    )


class CheckoutChoice(BaseModel):
    interval: str


@router.post("/checkout")
def checkout(choice: CheckoutChoice, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _, client = _configured()
    _customer_user(user)
    user = lock_owner(db, user.id)
    db.refresh(user)
    _customer_user(user)
    price = _price(client, choice.interval)
    origin = os.getenv("SR1_FRONTEND_ORIGIN", "")
    if not origin.startswith("https://"):
        raise HTTPException(503, "Billing prices or return URL are not configured")
    if user.stripe_subscription_id and user.subscription_status not in ("canceled", "incomplete_expired"):
        raise HTTPException(409, "Manage the existing subscription in the billing portal")
    if not user.stripe_customer_id:
        customer = client.v1.customers.create(
            params={"metadata": {"sr1_user_id": user.id},
                    **({"email": user.email} if user.email and not user.email.endswith("@auth0.local") else {})},
            options={"idempotency_key": f"sr1-customer-{user.id}"},
        )
        user.stripe_customer_id = customer.id
        # Keep the customer mapping even if Checkout times out. A retry must
        # inspect this same customer's sessions/subscriptions before charging.
        db.commit()
        user = lock_owner(db, user.id)
        db.refresh(user)
        _customer_user(user)
    # The workspace lock serializes concurrent clicks. Consult Stripe as the
    # webhook for a completed checkout may not have arrived yet.
    subscriptions = client.v1.subscriptions.list(params={"customer": user.stripe_customer_id, "status": "all", "limit": 100})
    for existing in subscriptions.auto_paging_iter():
        if existing["status"] not in ("canceled", "incomplete_expired"):
            db.commit()  # Preserve the customer for access to the portal.
            raise HTTPException(409, "A subscription already exists. Manage it in the billing portal")
    sessions = client.v1.checkout.sessions.list(params={"customer": user.stripe_customer_id, "status": "open", "limit": 100})
    for existing in sessions.auto_paging_iter():
        existing = _data(existing)
        if existing.get("client_reference_id") != user.id or existing.get("mode") != "subscription":
            continue
        if existing.get("metadata", {}).get("sr1_price_id") == price:
            db.commit()
            return {"url": existing["url"]}
        client.v1.checkout.sessions.expire(existing["id"])
    suffix = "".join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    session = client.v1.checkout.sessions.create(
        params={"mode": "subscription", "customer": user.stripe_customer_id,
                "line_items": [{"price": price, "quantity": 1}],
                "client_reference_id": user.id,
                "metadata": {"sr1_price_id": price},
                "integration_identifier": f"smartrisk_sr1_{suffix}",
                "subscription_data": {"metadata": {"sr1_user_id": user.id}},
                "success_url": f"{origin.rstrip('/')}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
                "cancel_url": f"{origin.rstrip('/')}/billing/cancel"},
    )
    db.commit()
    return {"url": session.url}


@router.post("/portal")
def portal(user: User = Depends(get_current_user)):
    _, client = _configured()
    _customer_user(user)
    origin = os.getenv("SR1_FRONTEND_ORIGIN", "")
    if not user.stripe_customer_id or not origin.startswith("https://"):
        raise HTTPException(400, "No billing account")
    configuration = os.getenv("STRIPE_PORTAL_CONFIGURATION")
    if not configuration:
        raise HTTPException(503, "Billing portal is not configured")
    session = client.v1.billing_portal.sessions.create(
        params={"customer": user.stripe_customer_id, "configuration": configuration,
                "return_url": f"{origin.rstrip('/')}/billing"}
    )
    return {"url": session.url}


@router.get("/status")
def status(user: User = Depends(get_current_user)):
    owner = getattr(user, "billing_owner", None) or user
    return {
        "plan": get_user_plan(user),
        "subscription_status": owner.subscription_status,
        "trial_ends_at": owner.trial_ends_at,
        "is_billing_owner": not bool(user.team_owner_id),
        "has_billing_account": bool(owner.stripe_customer_id),
    }


def _apply_subscription(user, subscription, client):
    # A delayed cancellation for a previous subscription must not revoke a
    # newer subscription. Fetch current state, then compare creation dates.
    subscription = _data(subscription)
    if user.stripe_subscription_id and user.stripe_subscription_id != subscription["id"]:
        previous = client.v1.subscriptions.retrieve(user.stripe_subscription_id)
        if previous["created"] > subscription["created"]:
            return
    user.stripe_subscription_id = subscription["id"]
    user.subscription_status = subscription["status"]
    user.plan = PLAN_PRO if _paid_status(subscription) else PLAN_LITE


@router.post("/stripe/webhook")
async def webhook(request: Request, stripe_signature: str = Header(default=""), db: Session = Depends(get_db)):
    stripe, client = _configured(webhook=True)
    try:
        event = stripe.Webhook.construct_event(
            await request.body(), stripe_signature, os.environ["STRIPE_WEBHOOK_SECRET"]
        )
    except (ValueError, stripe.SignatureVerificationError):
        raise HTTPException(400, "Invalid webhook signature")
    event = _data(event)
    if bool(event.get("livemode")) != (os.getenv("ENABLE_LIVE_BILLING", "false").lower() == "true"):
        raise HTTPException(400, "Webhook mode does not match billing environment")
    if db.get(BillingEvent, event["id"]):
        return {"received": True}
    kind = event["type"]
    obj = event["data"]["object"]
    customer_id = obj.get("customer")
    if kind in ("checkout.session.completed", "checkout.session.async_payment_succeeded") and obj.get("mode") == "subscription" and obj.get("payment_status") == "paid":
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user and obj.get("subscription"):
            user = lock_owner(db, user.id)
            db.refresh(user)
            subscription = client.v1.subscriptions.retrieve(obj["subscription"])
            _apply_subscription(user, subscription, client)
    elif kind in ("customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"):
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user = lock_owner(db, user.id)
            db.refresh(user)
            # Fetch current state to protect against out-of-order Stripe events.
            subscription = client.v1.subscriptions.retrieve(obj["id"])
            _apply_subscription(user, subscription, client)
    elif kind in ("invoice.paid", "invoice.payment_failed") and customer_id:
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user and user.stripe_subscription_id:
            user = lock_owner(db, user.id)
            db.refresh(user)
            subscription = _data(client.v1.subscriptions.retrieve(user.stripe_subscription_id))
            current_invoice_id = subscription.get("latest_invoice")
            failed_current_invoice = kind == "invoice.payment_failed" and obj["id"] == current_invoice_id
            if failed_current_invoice:
                invoice = _data(client.v1.invoices.retrieve(current_invoice_id))
                # A delayed failure event must not undo a recovered payment.
                failed_current_invoice = invoice.get("status") != "paid"
            user.subscription_status = "past_due" if failed_current_invoice else subscription["status"]
            user.plan = PLAN_LITE if failed_current_invoice else (PLAN_PRO if _paid_status(subscription) else PLAN_LITE)
    # Always record signed events, including events for unrelated customers.
    db.add(BillingEvent(id=event["id"]))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if not db.get(BillingEvent, event["id"]):
            raise
    return {"received": True}
