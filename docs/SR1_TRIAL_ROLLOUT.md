# SR1 customer signup and Stripe rollout

Status: implemented in draft PR #1; not deployed or ready for live payment acceptance.

## Offer

| Plan | Price | Limits |
|---|---|---|
| Trial | Free for 14 days, no card | One user, one project |
| Team monthly | €399 per month | Five users including owner; three shared projects |
| Team annual | €3,990 per year | Same limits; charged yearly |
| Guided pilot | By quote, 30 days | Sales-led evaluation |

Subscriptions renew automatically. Configure portal cancellation at the end of the current paid period. Payment failure restricts paid features until recovery. Saved projects are retained through expiry/cancellation and restored on reactivation. There is no automated deletion of saved work in this change.

All existing projects count toward the limit; there is no archive workflow. A sample project uses one slot. Members share the owner's projects; personal trial projects are retained but hidden while the person belongs to a team. Invitations reserve one of four member seats for seven days, are bound to a verified email, and are single-use. Owners copy invitation links; this change does not send invitation emails.

## Implemented

- Auth0 signup at `/create-account`, verified email claims, return login, session-token refresh for API callers, and helpful profile errors.
- Server-controlled trial dates and shared project/seat limits, including reservations serialized with a workspace database lock.
- First-project screen with a saved, editable sample FMEA or blank project choice.
- `/billing` plan comparison, payment-confirmation polling, owner-only Checkout/portal, and `/team` management.
- Stripe SDK 15.6.0 Checkout and portal, exact EUR price/interval checks, open-session reuse, and duplicate-subscription blocking.
- Signed webhook verification, environment checks, durable event replay protection, current subscription retrieval, and protection against a delayed cancellation of an older subscription.
- Trial expiry and failed/canceled subscriptions restrict access through a shared product API dependency; account and billing routes remain available for renewal/cancellation. Redirects alone never grant a plan.
- Production rejects old demo tokens when customer trials are enabled. Migrate legitimate demo accounts before switching.
- SQLite migration and PostgreSQL migration; duplicate index definitions that broke fresh-database creation are fixed.

## Render prerequisites and verified deployment state

Render connector access is working as of 2026-09-29. Both SR1 services deploy `JMSpanoman/fmea-ai`, branch `main`, using the corresponding Dockerfile with automatic deployment enabled.

- Frontend: `fmea-frontend-dczh`, service `srv-d35rg2juibrs73diuctg`, currently live on `768bca79b6b8faf71b9e26d16664a80df51dff81`.
- Backend: `fmea-backend-dczh`, service `srv-d35rg2juibrs73diucu0`. Latest deployment of `768bca79...` failed; the last live version is `9d746e109b6ea00a3c6e345ec56cf3831e54d98c`.
- Backend has a 1 GB persistent disk `dsk-dak6b4m1egvs7399fobg` mounted at `/app/db`. Preserve this mount and its database during rollout.
- Logs identify a Python 3.9/FastAPI annotation failure and a missing `db.runtime_migrations` import because the data disk hides that source directory. This draft upgrades the Docker runtime to Python 3.11 and moves migrations to `schema_migrations.py`, outside the data mount. Schema failures now stop startup.

Before deployment:

1. Back up the current database. Use a separate database and Render environment for the sandbox acceptance test.
2. Verify the current environment variables through Render settings; the connector exposes updates but not secret reads.
3. Do not merge until the acceptance prerequisites below are complete; merging `main` automatically deploys both services.
4. Apply `fmea_backend/migrations/add_user_trial_dates.sql` for PostgreSQL; SQLite migrates at startup. Do not bypass a duplicate-identity or migration failure.
5. Configure Auth0 and Stripe in the isolated environment, then perform the acceptance test below. Production stays on the current version until this passes.

## Auth0 setup

Create/verify a Single Page Application and API identifier. The API uses RS256. Configure the customer origin as **Allowed Callback URLs**, **Allowed Logout URLs**, and **Allowed Web Origins**. For production this is `https://fmea-frontend-dczh.onrender.com`; add the exact sandbox origin separately.

Deploy `docs/auth0/sr1-email-claims.js` as an Auth0 post-login Action and attach it to the Login flow. The access token must include the namespaced email and `email_verified: true`. A user verifies their email and signs in again before the 14-day trial starts. Do not substitute an unverified client email for these claims. Auth0 tenant/application access has not yet been verified.

Frontend Docker build variables (public values, then rebuild):

```dotenv
VITE_AUTH0_DOMAIN=YOUR_AUTH0_DOMAIN
VITE_AUTH0_CLIENT_ID=YOUR_SPA_CLIENT_ID
VITE_AUTH0_AUDIENCE=YOUR_API_IDENTIFIER
BACKEND_URL=https://YOUR_SANDBOX_BACKEND
```

Backend settings for isolated acceptance tests:

```dotenv
ENVIRONMENT=staging
AUTH0_DOMAIN=YOUR_AUTH0_DOMAIN
API_AUDIENCE=YOUR_API_IDENTIFIER
ENABLE_SELF_SERVICE_TRIALS=true
ALLOW_DEV_LOGIN=false
SMARTRISK_DEV_FORCE_PRO=false
CORS_ORIGINS=https://YOUR_SANDBOX_FRONTEND
SR1_FRONTEND_ORIGIN=https://YOUR_SANDBOX_FRONTEND
ENABLE_SR1_BILLING=true
ENABLE_LIVE_BILLING=false
STRIPE_PRICE_MONTHLY=YOUR_SANDBOX_MONTHLY_PRICE_ID
STRIPE_PRICE_YEARLY=YOUR_SANDBOX_YEARLY_PRICE_ID
```

Set `STRIPE_RESTRICTED_KEY` (preferred) and `STRIPE_WEBHOOK_SECRET` through Render secret environment settings. Never add actual secrets to this document, git, chat, or frontend build arguments. The fallback key variable is `STRIPE_SECRET_KEY`. The restricted key must allow the integration's Customer, Price, Subscription, Checkout Session, invoice-read, and billing-portal operations. `ENABLE_LIVE_BILLING` must match the key's mode; separate sandbox/live secrets and resources.

## Stripe setup still required

1. Expose a Stripe sandbox through the connected account. The connector currently returns only Foton Consulting **live** account `acct_1U8pGb2NDAwXFR5E`.
2. Create the sandbox Team product and exact recurring EUR prices: 39,900 cents every month and 399,000 cents every year, quantity one per team.
3. Confirm inclusive/exclusive tax treatment and applicable Stripe Tax registrations before activation. Automatic Tax has not been enabled.
4. Configure the customer portal: payment-method updates, invoice history, cancellation at period end. Restrict subscription changes to supported Team prices/quantity; verify the displayed renewal and cancellation terms.
5. Create a signed webhook destination at `https://YOUR_BACKEND/billing/stripe/webhook`, with:
   - `checkout.session.completed`
   - `checkout.session.async_payment_succeeded`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
6. Enter the sandbox API key, signing secret and price IDs in Render. Confirm webhook deliveries return 2xx and the app status follows Stripe.

Inactive live catalog already prepared, awaiting validation:

- Product `prod_VLVYE5BsLd8IuV` — SmartRisk 1 Team.
- Monthly `price_1UKoXi2NDAwXFR5Ex8FPrsSg` — €399/month, lookup `sr1_team_eur_monthly`.
- Annual `price_1UKoY52NDAwXFR5EAP7AoIQH` — €3,990/year, lookup `sr1_team_eur_yearly`.
- Product and both prices are inactive. No live payment was taken. Tax behavior remains unspecified.

## Verification completed locally

```sh
PYTHONPATH=fmea_backend python -m pytest -q --disable-warnings \
  fmea_backend/tests/test_trial_entitlement.py \
  fmea_backend/tests/test_team_access.py \
  fmea_backend/tests/test_billing_lifecycle.py \
  fmea_backend/tests/test_sr1_checkout.py \
  fmea_backend/tests/test_customer_startup.py
npm test --prefix frontend -- src/pages/BillingPage.test.tsx
npm run build --prefix frontend
```

Install the pinned backend requirements first; `test_sr1_checkout.py` uses the actual Stripe SDK. Stripe HTTP responses are simulated; signature verification uses the real SDK and test HMAC signatures. These are local regression checks, not proof of a real Stripe payment or deployed Auth0 login.

Last run: **18 backend tests passed on Python 3.11 with the pinned requirements; five frontend tests passed; production frontend build passed**. The startup test imports the full application, creates the commercial schema, preserves a saved identity across restart, rejects anonymous/demo access in customer mode, and fails startup on a migration error. This is not a Docker image or deployed-environment test. The baseline main branch reports 96 TypeScript errors; this branch reports 95, with no new diagnostics compared with that baseline; no errors are reported in the new signup/billing/team screens or changed API helper. These need a separate baseline cleanup and are not represented as a passing typecheck.

## Deployed acceptance test — not yet run

Use an isolated database, sandbox Stripe resources, and newly created verified Auth0 identities:

1. Open marketing Try SmartRisk 1, sign up, verify email, and sign in. Check trial start/end and no card request.
2. Create a sample project; edit a row, reload, sign out, sign in, and verify the saved work. Reject a second project during the trial.
3. Choose each plan from comparison; inspect EUR total/interval and billing terms at Checkout. Return via cancel; keep trial/work.
4. Complete a successful sandbox payment. Verify the signed webhook, active subscription, five-seat entitlement, and the same saved project.
5. Invite four verified emails, reject a sixth seat, reject wrong-email/expired/replayed invitations, share the three-project quota, and verify removal revokes project access.
6. Test a declined initial payment, repeated checkout clicks, delayed payment confirmation, a failed renewal, recovery, and replay/out-of-order events. Match Stripe state to backend access.
7. Cancel at period end: preserve access until the paid term ends, then restrict it while retaining work. Also exercise immediate cancellation in the sandbox.
8. Verify trial expiry, direct API gating, owner/member return login, project isolation, CORS, and backend restart persistence.
9. After acceptance passes, configure the equivalent live resources and tax treatment, activate prices, deploy, and verify public signup and checkout links. Keep a database backup and a rollback plan for code/environment changes.
