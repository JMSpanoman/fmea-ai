# SR1 customer signup and Stripe rollout

Status: implemented in draft PR #1 and deployed to an isolated Render sandbox. Fresh signup, verified-email login, sample-project creation, app-created monthly Checkout, declined/successful test payments, active Stripe subscription, and actual Stripe webhook delivery have been verified. The tester has confirmed Subscription: active in SR1 after the Check access correction. The tester also confirmed saved edits survive sign-out/return login and the app-created Stripe portal opens. Scheduled cancellation at the paid period end and retained project access afterward are verified. The Team owner can create three projects and receives a limit message on the fourth; server logs confirm two new creations (201) and the rejected attempt (403). Invitation reservation/revocation and the five-seat button limit have passed. Stripe termination/webhook delivery, app access cutoff, leaving Checkout without payment, and reactivation with saved edits are verified; remaining acceptance checks are pending; production is not ready for live payment acceptance. See `docs/SR1_SESSION_CHECKPOINT.md` for the latest saved checkpoint.

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

The isolated Blueprint was created on 2026-09-29. Both Docker services deployed commit `c5021e2` successfully and returned HTTP 200 from `/health`:

- Frontend: `https://sr1-sandbox-frontend-dczh.onrender.com`
- Backend: `https://sr1-sandbox-backend-dczh.onrender.com`

The backend uses its own persistent SQLite disk and staging settings. Its AI key is not configured; sample-project and billing acceptance do not require one. No existing production service was changed.

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
- The production and actual assigned sandbox frontend origins are registered for callbacks, logout, web origins, and allowed origins. A fresh tester signed up, verified their email, and signed in through the sandbox. Auth0 reports the identity as verified, and the backend accepted the real token at `/auth/me` at 2026-09-29 22:36:57 UTC.

Fresh-account verification succeeded in the development tenant; its email setup has not been accepted for production delivery. Signup requires the tester to choose a password and verify their email; do not bypass verification or replace this check with a pre-verified administrative identity.

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

Required restricted-key permissions for this implementation:

| Resource | Permission |
|---|---|
| Prices | Read |
| Customers | Write |
| Checkout Sessions | Write |
| Subscriptions | Read |
| Invoices | Read |
| Customer/Billing Portal | Write |

Set other permissions to None unless another documented operation needs them. The initial deployed checkout failed because Prices Read and then Subscriptions Read were missing. The owner edited the existing sandbox key in Stripe; successful app-created Checkout was subsequently verified. Editing that same key's permissions did not require replacing the Render secret. Subscription retrieval through the webhook and app-created portal access have since passed. On 30 September at 23:56 Athens, the renewal-decline test confirmed that Invoices Read is missing: invoice webhooks returned 500 with an explicit invoice_read permission error. The subscription event still set past_due and project access returned 403. The owner enabled Invoices Read on the existing key. A fresh 0341 sandbox decline then produced webhook 200 at 21:08:18.935 UTC, with no application error. Recovery paid the same invoice using the 4242 test card at 21:11:41 UTC; Stripe returned to active and two recovery webhooks returned 200. The tester still needs to confirm saved-project access after this recovery. No key value was displayed or replaced.

### Create the isolated Render environment

`render.sandbox.yaml` defines two new Docker services from the draft branch and a separate 1 GB SQLite disk. The backend needs the paid Starter plan for persistent disk storage; the frontend uses the free plan. This file does not manage existing production services. Automatic code deploys are off during acceptance.

1. Open a new Render Blueprint for this repository. Select branch `feature/sr1-trial-foundation` and Blueprint Path `render.sandbox.yaml`. Do not use the production `render.yaml`.
2. Enter the **sandbox** restricted API key (starting `rk_test_`) in the `STRIPE_RESTRICTED_KEY` secret field. Review the displayed resource cost and deploy the Blueprint. Never paste the key into chat or git.
3. Compare the actual assigned URLs with the two planned sandbox URLs in the file. If Render adds a suffix, update `BACKEND_URL`, `CORS_ORIGINS`, `SR1_FRONTEND_ORIGIN`, and this Blueprint before testing. Add the actual frontend origin to the Auth0 callback/logout/web-origin lists, preserving the existing origin.
4. For a new environment, create its Stripe sandbox webhook and provide both secret fields before enabling billing. The existing sandbox webhook has been created and its signing secret stored; the Blueprint now preserves the enabled sandbox-billing setting. Live billing stays disabled.
5. Trigger new sandbox deploys after configuration changes, check health and signed webhook delivery, then run the acceptance checklist.

The Blueprint was checked against Render's published JSON Schema locally and was successfully deployed through Render's Dashboard. The assigned URLs match the file. The connected Render tool cannot create Docker services, so future initial Blueprint creation requires the Dashboard. AI-generation acceptance additionally requires a separate sandbox `OPENAI_API_KEY`; the saved sample-project and billing checks do not use it.

## Stripe sandbox configuration — verified 2026-09-29

- The sandbox is connected. The SmartRisk 1 Team product has active recurring EUR prices: 39,900 cents per month and 399,000 cents per year, quantity one per team. Lookup keys are `sr1_team_eur_monthly` and `sr1_team_eur_yearly`.
- The default sandbox customer portal permits payment-method updates, invoice history, and cancellation at the end of the paid period. Plan and quantity changes are disabled pending their own acceptance tests.
- Stripe accepted a subscription Checkout Session for each price with the expected EUR total and accepted a portal session using this configuration. These checks used a synthetic sandbox customer without a real email address. No payment was completed and no app entitlement was granted. The test sessions will expire automatically.
- Both sandbox prices now use `tax_behavior=exclusive`. The inactive live prices also use exclusive tax behavior.
- Tax settings in both environments are pending: no head office, default product tax code, or tax registrations are configured. Automatic Tax remains off. On 30 September at 22:55 Athens, the owner confirmed Foton's business is in the United States with no current VAT or sales-tax registrations. This does not establish a tax exemption or determine registration obligations. Do not add a registration or enable tax collection without a confirmed applicable registration; never infer one from the owner's personal location.
- The live catalog remains inactive. No real payment has been taken.
- The sandbox webhook is enabled at `https://sr1-sandbox-backend-dczh.onrender.com/billing/stripe/webhook`, pinned to API version `2026-08-26.dahlia`. Its signing secret was transferred directly into the sandbox backend's Render environment. No secret is stored in this repository.
- The backend redeployed successfully with sandbox billing enabled. Deployed HTTP checks accepted a signed synthetic probe and its replay (200), rejected an invalid signature (400), and rejected a correctly signed live-mode probe (400). These checks confirm signing-secret wiring and mode/replay handling. They do not prove Stripe-origin payment delivery, restricted-key API permissions, or account entitlement changes.
- At 2026-09-29 23:00:40 UTC, `/billing/checkout` returned 200 using the application's restricted key. Stripe confirms an app-linked subscription Checkout Session with EUR 399 total (39,900 cents), `livemode=false`, and the correct sandbox return flow. The tester's screenshot shows SmartRisk 1 Team at EUR 399 per month and a Sandbox badge.
- The tester completed an insufficient-funds decline followed by a successful EUR 399 sandbox payment at 23:08:18 and 23:08:43 UTC, respectively. Stripe confirms Checkout is complete/paid and the app-linked subscription is active, with quantity one of the approved monthly price. Three Stripe-origin webhook requests returned 200 at 23:08:46–23:08:47 UTC, with no backend errors in this window. The tester subsequently confirmed Subscription: active in SR1 at 2026-09-30 02:33 Athens after the Check access correction. At 02:37 Athens, the tester confirmed saved-work retention after return login and the app-created portal opened; POST `/billing/portal` returned 200 at 23:36:57 UTC. At 02:40 Athens, the tester reported cancellation. Stripe confirms an explicit cancellation timestamp matching the paid period end (30 October 01:08 Athens), while status remains active. A Stripe-origin webhook returned 200 at 23:37:31 UTC and the original project/documents returned 200 at 23:40:22–23:40:23 UTC. At 02:45 Athens, the tester confirmed the fourth project was blocked. Server logs show two new projects created with 201 at 23:44:33 and 23:44:50 UTC, then a fourth-project attempt rejected with 403 at 23:45:04 UTC. The later invitation reservation/revocation UI test passed. Accepted-member sharing, forced API over-limit rejection, still require deployed acceptance. Post-termination app access cutoff and reactivation with retained work subsequently passed.

Acceptance follow-up:

1. Saved edits after sign-out/return login and the three-project Team owner limit have passed. At 1 October 00:33 Athens the tester also reported the five-step second-account flow passed: verified signup, one-project trial limit, invitation acceptance, shared access and member removal. That latest result is tester-confirmed; the currently available server logs do not independently corroborate the new second-account requests. Member shared-quota enforcement has passed locally through the full HTTP route journey.
2. Invoices Read is now corrected and verified by a fresh failed-payment webhook 200. The same renewal invoice is paid and Stripe is active with recovery webhooks 200. Confirm the tester can reopen the saved project after this recovery. Opening the app-created customer portal and scheduled cancellation with a successful webhook have passed. Initial declined/successful payments and subscription retrieval through the webhook have passed. Connector authorization is separate from the application's API credentials; the available connector operations cannot issue or edit that key.
3. Verify Stripe delivery and access transitions for the configured event subscriptions:
   - `checkout.session.completed`
   - `checkout.session.async_payment_succeeded`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
4. Verify 2xx deliveries and that app access follows Stripe. Never publish API keys or signing secrets in source.
5. Complete the deployed acceptance test below. Successful session creation is not proof of payment, webhook delivery, or the full account-to-access journey.

## Verification completed locally

```sh
PYTHONPATH=fmea_backend python -m pytest -q --disable-warnings \
  fmea_backend/tests/test_trial_entitlement.py \
  fmea_backend/tests/test_team_access.py \
  fmea_backend/tests/test_billing_lifecycle.py \
  fmea_backend/tests/test_sr1_checkout.py \
  fmea_backend/tests/test_customer_startup.py \
  fmea_backend/tests/test_schema_backup.py \
  fmea_backend/tests/test_customer_access_journey.py
npm test --prefix frontend -- src/pages/BillingPage.test.tsx
npm run build --prefix frontend
```

Install the pinned backend requirements first; `test_sr1_checkout.py` uses the actual Stripe SDK. Stripe HTTP responses are simulated; signature verification uses the real SDK and test HMAC signatures. These are local regression checks, not proof of a real Stripe payment or deployed Auth0 login.

Last run: **21 backend tests passed on Python 3.11 with the pinned requirements; eight frontend tests passed; production frontend build passed**. Hosted SQLite startup now verifies a private backup on the persistent disk before schema writes; backup or integrity failures stop startup. The startup test imports the full application, creates the commercial schema, preserves a saved identity across restart, rejects anonymous/demo access in customer mode, and fails startup on a migration error. This is not a Docker image or deployed-environment test. The baseline main branch reports 96 TypeScript errors; this branch reports 95, with no new diagnostics compared with that baseline; no errors are reported in the new signup/billing/team screens or changed API helper. These need a separate baseline cleanup and are not represented as a passing typecheck.

## Deployed acceptance test — in progress

Latest final-check update (1 October): recovered account/project/document requests returned 200 at 00:18 Athens. Deployed anonymous-access, demo-login, unsigned-webhook and CORS probes passed. The new full-application local HTTP journey for invitations, sharing, member removal, quotas, payment-state access and trial expiry passed separately from the previous 21-test backend run. It uses a temporary database and test identities; the deployed second-account journey still requires a verified second email. Earlier pending-recovery wording below is historical and superseded by these observed project/document responses.

Update at 00:33 Athens: the owner reported all five second-account browser steps passed, superseding the pending second-account item above. Record it as tester-confirmed, not independently log-verified. Production email, secure live credentials/webhook, the reviewed production deployment, and public link activation remain outstanding. Do not repeat the passed manual test without a concrete new failure.

### Prepared production configuration

These are reviewed target values, not a claim that production currently uses them. Apply the complete configuration with the reviewed release; changing Render environment values immediately triggers deployment, including on the currently failing old main branch. Do not enable live checkout before required secrets, email delivery, backup and deployment are ready.

| Setting | Target value |
|---|---|
| Production backend | `srv-d35rg2juibrs73diucu0` |
| Production frontend | `srv-d35rg2juibrs73diuctg` |
| Live Stripe account | `acct_1U8pGb2NDAwXFR5E` |
| `STRIPE_PRICE_MONTHLY` | `price_1UKoXi2NDAwXFR5Ex8FPrsSg` — currently inactive |
| `STRIPE_PRICE_YEARLY` | `price_1UKoY52NDAwXFR5EAP7AoIQH` — currently inactive |
| `STRIPE_PORTAL_CONFIGURATION` | `bpc_1ULV0n2NDAwXFR5EQw3J8W3r` — prepared with the tested portal features |
| `SR1_FRONTEND_ORIGIN` / `CORS_ORIGINS` | `https://fmea-frontend-dczh.onrender.com` |
| Live webhook URL | `https://fmea-backend-dczh.onrender.com/billing/stripe/webhook` — not yet registered |
| `STRIPE_RESTRICTED_KEY` | Owner enters the live restricted key securely in Render; use the permission table above, including Invoices Read |
| `STRIPE_WEBHOOK_SECRET` | Securely provision the signing secret from the future live endpoint; never reuse the sandbox secret |
| Trial and account safety | `ENABLE_SELF_SERVICE_TRIALS=true`, `ALLOW_DEV_LOGIN=false`, `SMARTRISK_DEV_FORCE_PRO=false`, `DEMO_ENSURE_PROJECT=false`, `DEMO_REASSIGN_PROJECT=false` |
| Live activation | `ENABLE_SR1_BILLING=true` and `ENABLE_LIVE_BILLING=true` only for the completed production configuration with live secrets and active approved prices |

Production email requires an authenticated review of Auth0's email-provider settings and verified delivery of signup verification and password-reset messages. No provider or credentials were supplied or inferred. Existing demo data must be preserved and legitimate demo identities migrated deliberately before retiring the old login. The startup snapshot protects schema migration; maintain a separate off-service backup for disaster recovery.

Verified so far: fresh signup, verified email and signed-token API access, 14-day trial displayed, sample-project creation (201) and retrieval (200), plan comparison, opening monthly sandbox Checkout, declined/successful payments, active Stripe subscription, and actual Stripe webhook delivery (200). The tester also confirmed the active subscription display in SR1 after the Check access correction. Saved-edit persistence after return login and opening the app-created portal have passed by tester confirmation, with portal creation returning 200. Scheduled cancellation at the paid period end, a Stripe-origin webhook during the change, and retained project access afterward are verified. The three-project Team owner limit is verified by tester confirmation and server responses (two additional 201 creations, then 403 for the fourth attempt). On 30 September at 23:13 Athens, the tester confirmed four invitations disabled the creation button, revoking one enabled it again, and all test invitations were removed; backend responses corroborate four creations (201) and four revocations (204). The sandbox subscription was intentionally ended at 20:14:44 UTC and its webhook returned 200 at 20:14:45 UTC. The owner subsequently reported all cancellation/re-upgrade steps passed at 23:31 Athens: canceled status, blocked projects, leaving Checkout without paying, new successful monthly payment, active status and retained edits. The server returned 403 for projects while canceled and 200 for projects/documents after three successful webhooks for the replacement subscription. Stripe confirms that replacement is active and its app-linked EUR 399 monthly Checkout is complete/paid. The renewal-decline test subsequently produced past_due and a server-side project-access 403, confirmed by the tester. It also exposed a missing Invoices Read permission on the sandbox restricted key: the invoice handler returned 500 while the separate subscription event returned 200. That permission was corrected on 1 October around 00:01 Athens. A fresh 0341 decline returned webhook 200 at 21:08:18.935 UTC; recovery paid the same EUR 398.88 test-adjusted invoice with 4242 at 21:11:41 UTC. Stripe is active and two recovery webhooks returned 200. Post-recovery app display and saved-project access still await tester confirmation. Forced sixth-seat API rejection, member access to the shared quota, and expiry remain unverified in the deployed environment; existing local coverage is recorded separately.

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
