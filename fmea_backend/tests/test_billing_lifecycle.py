"""Exercise billing choices and signed event transitions without Stripe credentials."""
import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest
from fastapi import HTTPException

spec = importlib.util.spec_from_file_location("sr1_billing_test", Path(__file__).parents[1] / "routers" / "billing.py")
billing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(billing)


def subscription(status="active", price="price_month", invoice="in_1"):
    return {"id": "sub_1", "status": status, "latest_invoice": invoice,
            "items": {"data": [{"price": {"id": price}, "quantity": 1}]}}


class FakeDB:
    def __init__(self):
        self.user = SimpleNamespace(id="owner", stripe_customer_id="cus_1", stripe_subscription_id="sub_1", plan="lite", subscription_status=None)
        self.events = {}

    def get(self, model, key):
        return self.events.get(key)

    def query(self, model):
        return self

    def filter(self, predicate):
        return self

    def first(self):
        return self.user

    def add(self, event):
        self.events[event.id] = event

    def commit(self):
        pass


class FakeRequest:
    async def body(self):
        return b"signed payload"


def test_price_validation_prevents_wrong_currency_or_amount(monkeypatch):
    monkeypatch.setenv("STRIPE_PRICE_MONTHLY", "price_month")
    client = SimpleNamespace(v1=SimpleNamespace(prices=SimpleNamespace(
        retrieve=lambda key: SimpleNamespace(active=True, currency="eur", unit_amount=39900, tax_behavior="exclusive",
                                             recurring=SimpleNamespace(interval="month", interval_count=1)))))
    assert billing._price(client, "monthly") == "price_month"
    client.v1.prices.retrieve = lambda key: SimpleNamespace(active=True, currency="usd", unit_amount=39900, tax_behavior="exclusive",
                                                             recurring=SimpleNamespace(interval="month", interval_count=1))
    with pytest.raises(HTTPException) as exc:
        billing._price(client, "monthly")
    assert exc.value.status_code == 503


def test_only_active_configured_subscription_grants_access(monkeypatch):
    monkeypatch.setenv("STRIPE_PRICE_MONTHLY", "price_month")
    assert billing._paid_status(subscription())
    assert not billing._paid_status(subscription(status="canceled"))
    assert not billing._paid_status(subscription(price="price_other"))


def test_signed_webhook_activation_failure_cancellation_and_replay(monkeypatch):
    monkeypatch.setenv("ENABLE_SR1_BILLING", "true")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")
    monkeypatch.setenv("STRIPE_PRICE_MONTHLY", "price_month")
    current = subscription()
    event = {"id": "evt_1", "livemode": False, "type": "customer.subscription.created",
             "data": {"object": {"id": "sub_1", "customer": "cus_1"}}}
    stripe = SimpleNamespace(
        StripeClient=lambda key, **kwargs: SimpleNamespace(v1=SimpleNamespace(
            subscriptions=SimpleNamespace(retrieve=lambda key: current),
            invoices=SimpleNamespace(retrieve=lambda key: {"status": "open"}))),
        Webhook=SimpleNamespace(construct_event=lambda payload, sig, secret: event if sig == "valid" else (_ for _ in ()).throw(ValueError())),
        SignatureVerificationError=ValueError,
    )
    monkeypatch.setitem(sys.modules, "stripe", stripe)
    db = FakeDB()
    monkeypatch.setattr(billing, "lock_owner", lambda db, key: db.user)
    db.refresh = lambda user: None
    with pytest.raises(HTTPException) as exc:
        asyncio.run(billing.webhook(FakeRequest(), "invalid", db))
    assert exc.value.status_code == 400
    event = {"id": "evt_unpaid", "livemode": False, "type": "checkout.session.completed",
             "data": {"object": {"mode": "subscription", "payment_status": "unpaid",
                                 "subscription": "sub_1", "customer": "cus_1"}}}
    asyncio.run(billing.webhook(FakeRequest(), "valid", db))
    assert db.user.plan == "lite"
    event = {"id": "evt_1", "livemode": False, "type": "customer.subscription.created",
             "data": {"object": {"id": "sub_1", "customer": "cus_1"}}}
    asyncio.run(billing.webhook(FakeRequest(), "valid", db))
    assert db.user.plan == "pro"
    assert len(db.events) == 2
    asyncio.run(billing.webhook(FakeRequest(), "valid", db))
    assert len(db.events) == 2

    event = {"id": "evt_2", "livemode": False, "type": "invoice.payment_failed",
             "data": {"object": {"id": "in_1", "customer": "cus_1"}}}
    asyncio.run(billing.webhook(FakeRequest(), "valid", db))
    assert db.user.plan == "lite"
    assert db.user.subscription_status == "past_due"

    event = {"id": "evt_2b", "livemode": False, "type": "invoice.paid",
             "data": {"object": {"id": "in_1", "customer": "cus_1"}}}
    asyncio.run(billing.webhook(FakeRequest(), "valid", db))
    assert db.user.plan == "pro"
    assert db.user.subscription_status == "active"

    current = subscription(status="canceled")
    event = {"id": "evt_3", "livemode": False, "type": "customer.subscription.deleted",
             "data": {"object": {"id": "sub_1", "customer": "cus_1"}}}
    asyncio.run(billing.webhook(FakeRequest(), "valid", db))
    assert db.user.plan == "lite"
    assert db.user.subscription_status == "canceled"
