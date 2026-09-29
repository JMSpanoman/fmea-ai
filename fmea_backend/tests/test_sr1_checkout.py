"""Real database + real Stripe signature verification; Stripe HTTP is simulated."""
import asyncio
import hashlib
import hmac
import importlib.util
import json
import time
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import stripe
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models.user import User, BillingEvent
from models.fmea import FMEARow
from auth.plan import get_user_plan
from business_logic import team_access
from business_logic.sample_project import create_sample_project
from crud.user import create_user_from_auth0
from auth.security import create_dev_token, verify_auth0_token

spec = importlib.util.spec_from_file_location('sr1_checkout_test', Path(__file__).parents[1] / 'routers' / 'billing.py')
billing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(billing)


@pytest.fixture
def db():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as session:
        yield session


def test_sample_work_survives_expiry_upgrade_and_return_login(db):
    user = create_user_from_auth0(db, 'auth0|fresh', 'fresh@example.com', start_trial=True)
    trial_end = user.trial_ends_at
    assert trial_end - user.trial_started_at == timedelta(days=14)
    project = create_sample_project(db, user.id)
    rows = db.query(FMEARow).filter(FMEARow.project_id == project.id).all()
    assert len(rows) == 2
    rows[0].mitigation = 'Saved customer edit'; db.commit()
    with pytest.raises(HTTPException): create_sample_project(db, user.id)
    db.rollback()
    user.trial_ends_at = team_access.utcnow() - timedelta(seconds=1); db.commit()
    assert get_user_plan(user) == 'lite'
    user.plan = 'pro'; user.subscription_status = 'active'; db.commit()
    create_sample_project(db, user.id)
    project_id = project.id
    original_id = user.id
    db.expunge_all()
    returning = create_user_from_auth0(db, 'auth0|fresh', 'fresh@example.com', start_trial=True)
    assert returning.id == original_id
    assert returning.trial_ends_at < trial_end  # Returning does not restart the trial.
    assert get_user_plan(returning) == 'pro'
    assert db.query(FMEARow).filter(FMEARow.project_id == project_id, FMEARow.mitigation == 'Saved customer edit').count() == 1


def test_production_rejects_previously_issued_demo_token(monkeypatch):
    monkeypatch.setenv('JWT_SECRET_KEY', 'local-test-secret-that-is-only-for-tests')
    monkeypatch.setenv('ENVIRONMENT', 'development')
    token = create_dev_token(sub='dev:john@fotonconsulting.com', email='john@fotonconsulting.com')
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.setenv('ALLOW_DEV_LOGIN', 'true')
    monkeypatch.setenv('ENABLE_SELF_SERVICE_TRIALS', 'true')
    assert verify_auth0_token(token) is None


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('STRIPE_PRICE_MONTHLY', 'price_month')
    monkeypatch.setenv('STRIPE_PRICE_YEARLY', 'price_year')
    monkeypatch.setenv('STRIPE_WEBHOOK_SECRET', 'whsec_unit_test_only')
    monkeypatch.setenv('SR1_FRONTEND_ORIGIN', 'https://example.com')
    monkeypatch.setenv('STRIPE_PORTAL_CONFIGURATION', 'bpc_sr1_test')
    monkeypatch.setenv('ENABLE_LIVE_BILLING', 'false')
    client = Mock()
    client.v1.prices.retrieve.return_value = SimpleNamespace(active=True, currency='eur', unit_amount=39900, tax_behavior='exclusive',
        recurring=SimpleNamespace(interval='month', interval_count=1))
    client.v1.subscriptions.list.return_value.auto_paging_iter.return_value = []
    client.v1.checkout.sessions.list.return_value.auto_paging_iter.return_value = []
    monkeypatch.setattr(billing, '_configured', lambda **kwargs: (stripe, client))
    return client


def owner(db):
    user = User(id='owner', auth0_id='auth0|owner', email='owner@example.com', stripe_customer_id='cus_test')
    db.add(user); db.commit()
    return user


def test_checkout_reuses_open_session_and_blocks_duplicate_subscription(db, client):
    user = owner(db)
    sessions = client.v1.checkout.sessions
    sessions.create.return_value = SimpleNamespace(id='cs_1', url='https://checkout.stripe.com/test')
    assert billing.checkout(billing.CheckoutChoice(interval='monthly'), user, db)['url'].endswith('/test')
    params = sessions.create.call_args.kwargs['params']
    assert params['line_items'] == [{'price': 'price_month', 'quantity': 1}]
    assert params['mode'] == 'subscription'
    sessions.list.return_value.auto_paging_iter.return_value = [{'id': 'cs_1', 'mode': 'subscription',
        'client_reference_id': 'owner', 'metadata': {'sr1_price_id': 'price_month'}, 'url': 'https://checkout.stripe.com/test'}]
    billing.checkout(billing.CheckoutChoice(interval='monthly'), user, db)
    assert sessions.create.call_count == 1
    client.v1.subscriptions.list.return_value.auto_paging_iter.return_value = [{'id': 'sub_1', 'status': 'active'}]
    with pytest.raises(HTTPException) as error: billing.checkout(billing.CheckoutChoice(interval='monthly'), user, db)
    assert error.value.status_code == 409
    assert sessions.create.call_count == 1


def test_member_cannot_purchase_and_price_must_recur_every_one_month(db, client):
    user = owner(db)
    user.team_owner_id = 'someone_else'; db.commit()
    with pytest.raises(HTTPException): billing.checkout(billing.CheckoutChoice(interval='monthly'), user, db)
    client.v1.prices.retrieve.return_value.recurring.interval_count = 3
    with pytest.raises(HTTPException): billing._price(client, 'monthly')


def test_checkout_timeout_keeps_customer_mapping_for_retry(db, client):
    user = owner(db)
    user.stripe_customer_id = None; db.commit()
    client.v1.customers.create.return_value = SimpleNamespace(id='cus_persisted')
    client.v1.checkout.sessions.create.side_effect = TimeoutError('response timed out')
    with pytest.raises(TimeoutError):
        billing.checkout(billing.CheckoutChoice(interval='monthly'), user, db)
    db.rollback()
    db.refresh(user)
    assert user.stripe_customer_id == 'cus_persisted'
    client.v1.checkout.sessions.list.return_value.auto_paging_iter.return_value = [{
        'id': 'cs_created', 'mode': 'subscription', 'client_reference_id': user.id,
        'metadata': {'sr1_price_id': 'price_month'}, 'url': 'https://checkout.stripe.com/recovered'}]
    assert billing.checkout(billing.CheckoutChoice(interval='monthly'), user, db)['url'].endswith('/recovered')
    assert client.v1.customers.create.call_count == 1
    assert client.v1.checkout.sessions.create.call_count == 1


def test_checkout_rejects_inclusive_tax_and_portal_uses_sr1_configuration(db, client):
    user = owner(db)
    client.v1.prices.retrieve.return_value.tax_behavior = 'inclusive'
    with pytest.raises(HTTPException) as error:
        billing.checkout(billing.CheckoutChoice(interval='monthly'), user, db)
    assert error.value.status_code == 503
    db.rollback()
    client.v1.billing_portal.sessions.create.return_value = SimpleNamespace(url='https://billing.stripe.com/test')
    assert billing.portal(user)['url'] == 'https://billing.stripe.com/test'
    assert client.v1.billing_portal.sessions.create.call_args.kwargs['params']['configuration'] == 'bpc_sr1_test'


def subscription(id='sub_new', status='active', created=200):
    return {'id': id, 'created': created, 'status': status, 'latest_invoice': 'in_current',
        'items': {'data': [{'price': {'id': 'price_month'}, 'quantity': 1}]}}


def deliver(db, event, signature=None):
    payload = json.dumps(event).encode()
    timestamp = int(time.time())
    signed = str(timestamp).encode() + b'.' + payload
    signature = signature or f't={timestamp},v1={hmac.new(b"whsec_unit_test_only", signed, hashlib.sha256).hexdigest()}'
    class Request:
        async def body(self): return payload
    return asyncio.run(billing.webhook(Request(), signature, db))


def test_real_signature_webhooks_replay_and_old_cancellation(db, client):
    user = owner(db)
    client.v1.subscriptions.retrieve.side_effect = lambda key: subscription() if key == 'sub_new' else subscription('sub_old', 'canceled', 100)
    event = {'id': 'evt_new', 'object': 'event', 'livemode': False, 'type': 'customer.subscription.created',
        'data': {'object': {'id': 'sub_new', 'customer': 'cus_test'}}}
    with pytest.raises(HTTPException) as error: deliver(db, event, 't=0,v1=invalid')
    assert error.value.status_code == 400
    assert db.query(BillingEvent).count() == 0
    deliver(db, event); deliver(db, event)
    assert get_user_plan(user) == 'pro'
    assert db.query(BillingEvent).count() == 1
    event['id'] = 'evt_old'; event['type'] = 'customer.subscription.deleted'; event['data']['object']['id'] = 'sub_old'
    deliver(db, event)
    assert user.stripe_subscription_id == 'sub_new'
    assert get_user_plan(user) == 'pro'
    event['id'] = 'evt_live'; event['livemode'] = True
    with pytest.raises(HTTPException): deliver(db, event)
    assert db.query(BillingEvent).count() == 2


def test_real_sdk_payment_failure_recovery_and_period_end_cancellation(db, client):
    user = owner(db)
    user.trial_ends_at = team_access.utcnow() + timedelta(days=10)
    current = subscription()
    current['cancel_at_period_end'] = True
    invoice = {'id': 'in_current', 'status': 'open'}
    client.v1.invoices.retrieve.side_effect = lambda key: stripe.Invoice.construct_from(invoice, 'sk_test_unused')
    client.v1.subscriptions.retrieve.side_effect = lambda key: stripe.Subscription.construct_from(current, 'sk_test_unused')
    event = {'id': 'evt_active', 'object': 'event', 'livemode': False, 'type': 'customer.subscription.updated',
        'data': {'object': {'id': 'sub_new', 'customer': 'cus_test'}}}
    deliver(db, event)
    assert get_user_plan(user) == 'pro'  # Cancellation scheduled, period has not ended.
    event.update(id='evt_failed', type='invoice.payment_failed')
    event['data']['object']['id'] = 'in_current'
    deliver(db, event)
    assert get_user_plan(user) == 'lite'  # A remaining trial must not mask failed billing.
    current['status'] = 'active'
    invoice['status'] = 'paid'
    event.update(id='evt_recovered', type='invoice.paid')
    deliver(db, event)
    assert get_user_plan(user) == 'pro'
    event.update(id='evt_delayed_failure', type='invoice.payment_failed')
    deliver(db, event)
    assert get_user_plan(user) == 'pro'
    current['status'] = 'canceled'
    event.update(id='evt_canceled', type='customer.subscription.deleted')
    event['data']['object']['id'] = 'sub_new'
    deliver(db, event)
    assert get_user_plan(user) == 'lite'
