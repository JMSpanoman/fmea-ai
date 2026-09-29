# SR1 customer signup and Stripe rollout

Status: implemented in draft PR #1; not deployed or ready for live payment acceptance.

## Offer

| Plan | Price | Limits |
|---|---|---|
| Trial | Free for 14 days, no card | One user, one project |
| Team monthly | €399 per month | Five users including owner; three shared projects |
| Team annual | €3,990 per year | Same limits; charged yearly |
| Guided pilot | By quote, 30 days | Sales-led evaluation |

The monthly and annual prices exclude VAT, as approved by the owner. Tax-exclusive price configuration does not itself enable VAT calculation or collection.

Subscriptions renew automatically. Configure portal cancellation at the end of the current paid period. Payment failure restricts paid features until recovery. Saved projects are retained through expiry/cancellation and restored on reactivation. There is no automated deletion of saved work in this change.

All existing projects count toward the limit; there is no archive workflow. A sample project uses one slot. Members share the owner's projects; personal trial projects are retained but hidden while the person belongs to a team. Invitations reserve one of four member seats for seven days, are bound to a verified email, and are single-use. Owners copy invitation links; this change does not send invitation emails.

## Implemented

- Auth0 signup at `/create-account`, verified email claims, return login, session-token refresh for API callers, and helpful profile errors.
- Server-controlled trial dates and shared project/seat limits, including reservations serialized with a workspace database lock.
- First-project screen with a saved, editable sample FMEA or blank project choice.
- `/billing` plan comparison, payment-confirmation polling, owner-only Checkout/portal, and `/team` management.
- Stripe SDK 15.6.0 Checkout and portal, exact tax-exclusive EUR price/interval checks, open-session reuse, and duplicate-subscription blocking. Portal sessions use the explicitly configured SR1 portal configuration.
- Signed webhook verification, environment checks, durable event replay protection, current subscription retrieval, and protection against a delayed cancellation of an older subscription.
- Trial expiry and failed/canceled subscriptions restrict access through a shared product API dependency; account and billing routes remain available for renewal/cancellation. Redirects alone never grant a plan.
- Production rejects old demo tokens when customer trials are enabled. Migrate legitimate demo accounts before switching.
- SQLite migration and PostgreSQL migration; duplicate index definitions that broke fresh-database creation are fixed.

## Render prerequisites and verified deployment state

Render connector access is working as of 2026-09-29. The existing backend has a persistent database disk. Preserve and back up its contents before rollout.

Deployment diagnostics identified two startup problems: Python 3.9 cannot evaluate newer type annotations, and the data disk hides migration source code located below its mount path. This draft uses Python 3.11, moves migrations outside database storage, and stops startup on schema failures. These fixes remain on the draft branch.

Before deployment:

1. Back up the current database. Use a separate database and Render environment for the sandbox acceptance test.
2. Verify the current environment variables through Render settings; the connector exposes updates but not secret reads.
3. Do not merge until the acceptance prerequisites below are complete; merging `main` automatically deploys both services.
4. Apply `fmea_backend/migrations/add_user_trial_dates.sql` for PostgreSQL; SQLite migrates at startup. Do not bypass a duplicate-identity or migration failure.
5. Configure Auth0 and Stripe in the isolated environment, then perform the acceptance test below. Production stays on the current version until this passes.

## Auth0 setup

Create/verify a Single Page Application and API identifier. The API uses RS256. Configure the customer origin as **Allowed Callback URLs**, **Allowed Logout URLs**, and **Allowed Web Origins**. For production this is `https://fmea-frontend-dczh.onrender.com`; add the exact sandbox origin separately.

Auth0 access was connected and the configuration below was verified on 2026-09-29:

- The SmartRisk 1 first-party Single Page Application uses Authorization Code flow, RS256, and rotating refresh tokens. Browser tokens remain in memory.
- The SmartRisk 1 API has identifier `https://smartrisk.fotonconsulting.com/api`, RS256, a one-hour access-token lifetime, and offline access enabled for refresh tokens.
- Email/password signup is enabled for SR1. The default Google development connection is disabled for this application; other applications are unchanged.
- `docs/auth0/sr1-email-claims.js` is deployed on Node 22 and attached to the post-login flow. The backend requires its namespaced email and `email_verified: true`. Users verify their email and sign in again before their 14-day trial starts.
- The production frontend origin is registered for callbacks, logout, and web origins. A PKCE authorization request with the SR1 audience reached the expected `login_required` response, confirming that Auth0 accepts those settings. This does not verify an actual signup or token exchange.

After creating the isolated Render services, register the **actual assigned sandbox frontend origin** in Auth0 before testing. It is deliberately not allowlisted until Render confirms ownership. Verify email delivery with a fresh account; the tenant's development email setup has not been accepted for production delivery.

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
STRIPE_PORTAL_CONFIGURATION=YOUR_SANDBOX_PORTAL_CONFIGURATION_ID
```

Set `STRIPE_RESTRICTED_KEY` (preferred) and `STRIPE_WEBHOOK_SECRET` through Render secret environment settings. Never add actual secrets to this document, git, chat, or frontend build arguments. The fallback key variable is `STRIPE_SECRET_KEY`. The restricted key must allow the integration's Customer, Price, Subscription, Checkout Session, invoice-read, and billing-portal operations. `ENABLE_LIVE_BILLING` must match the key's mode; separate sandbox/live secrets and resources.

### Create the isolated Render environment

`render.sandbox.yaml` defines two new Docker services from the draft branch and a separate 1 GB SQLite disk. The backend needs the paid Starter plan for persistent disk storage; the frontend uses the free plan. This file does not manage existing production services. Automatic code deploys are off during acceptance.

1. Open a new Render Blueprint for this repository. Select branch `feature/sr1-trial-foundation` and Blueprint Path `render.sandbox.yaml`. Do not use the production `render.yaml`.
2. Enter the **sandbox** restricted API key (starting `rk_test_`) in the `STRIPE_RESTRICTED_KEY` secret field. Review the displayed resource cost and deploy the Blueprint. Never paste the key into chat or git.
3. Compare the actual assigned URLs with the two planned sandbox URLs in the file. If Render adds a suffix, update `BACKEND_URL`, `CORS_ORIGINS`, `SR1_FRONTEND_ORIGIN`, and this Blueprint before testing. Add the actual frontend origin to the Auth0 callback/logout/web-origin lists, preserving the existing origin.
4. Create the Stripe sandbox webhook listed below, store its signing secret on the sandbox backend, and enable `ENABLE_SR1_BILLING` only after all billing settings are present. Update the Blueprint flag too, so a later sync cannot undo the tested configuration.
5. Trigger new sandbox deploys after configuration changes, check health and signed webhook delivery, then run the acceptance checklist.

The Blueprint was checked against Render's published JSON Schema locally. Render's Dashboard must still validate account availability, service plans, repository access, and assigned URLs. The connected Render tool cannot create Docker services, so initial Blueprint creation requires the Dashboard. No sandbox resources have been provisioned by this file alone. AI-generation acceptance additionally requires a separate sandbox `OPENAI_API_KEY`; the saved sample-project and billing checks do not use it.

## Stripe sandbox configuration — verified 2026-09-29

- The sandbox is connected. The SmartRisk 1 Team product has active recurring EUR prices: 39,900 cents per month and 399,000 cents per year, quantity one per team. Lookup keys are `sr1_team_eur_monthly` and `sr1_team_eur_yearly`.
- The default sandbox customer portal permits payment-method updates, invoice history, and cancellation at the end of the paid period. Plan and quantity changes are disabled pending their own acceptance tests.
- Stripe accepted a subscription Checkout Session for each price with the expected EUR total and accepted a portal session using this configuration. These checks used a synthetic sandbox customer without a real email address. No payment was completed and no app entitlement was granted. The test sessions will expire automatically.
- Both sandbox prices now use `tax_behavior=exclusive`. The inactive live prices also use exclusive tax behavior.
- Tax settings in both environments are pending: no head office, default product tax code, or tax registrations are configured. Automatic Tax remains off. Record the owner's confirmed tax setup and applicable registrations before enabling tax calculation; never infer a registration from the owner's personal location.
- The live catalog remains inactive. No real payment has been taken.

Still required:

1. Deploy `render.sandbox.yaml`, register its actual frontend origin in the configured Auth0 application, and verify signup/email delivery.
2. Store the sandbox restricted API key in Render. Connector authorization is separate from the application's API credentials; the available connector operations cannot issue that key.
3. Create the signed webhook destination when the isolated backend URL is available: `https://YOUR_BACKEND/billing/stripe/webhook`, subscribing to:
   - `checkout.session.completed`
   - `checkout.session.async_payment_succeeded`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
4. Store its signing secret, sandbox price IDs, and the sandbox SR1 portal configuration ID in Render. Verify 2xx deliveries and that app access follows Stripe. Never publish API keys or signing secrets in source.
5. Complete the deployed acceptance test below. Successful session creation is not proof of payment, webhook delivery, or the full account-to-access journey.

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

Last run: **19 backend tests passed on Python 3.11 with the pinned requirements; five frontend tests passed; production frontend build passed**. The startup test imports the full application, creates the commercial schema, preserves a saved identity across restart, rejects anonymous/demo access in customer mode, and fails startup on a migration error. This is not a Docker image or deployed-environment test. The baseline main branch reports 96 TypeScript errors; this branch reports 95, with no new diagnostics compared with that baseline; no errors are reported in the new signup/billing/team screens or changed API helper. These need a separate baseline cleanup and are not represented as a passing typecheck.

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
