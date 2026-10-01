# SR1 production readiness

Checkpoint: 1 October 2026, Europe/Athens.

## Saved configuration; no production deployment

The existing production Render backend and frontend were inspected through the authenticated dashboard. The backend still uses the legacy demo configuration. Its last successful release is older than current main; the latest attempted deployment failed with a Python 3.9 type-annotation error. The tested release uses Python 3.11 and includes the separate migration/backup fixes. Do not redeploy old main as a launch step.

The following non-secret settings were added using Render's **Save only** option:

| Service | Settings saved |
| --- | --- |
| Backend | `AUTH0_DOMAIN`, `API_AUDIENCE`, `SR1_FRONTEND_ORIGIN`, approved live monthly/yearly price references, and the prepared live billing-portal configuration reference |
| Backend gates | `ENABLE_SELF_SERVICE_TRIALS=false`, `ENABLE_SR1_BILLING=false`, `ENABLE_LIVE_BILLING=false` |
| Frontend | `VITE_AUTH0_DOMAIN`, `VITE_AUTH0_CLIENT_ID`, `VITE_AUTH0_AUDIENCE` for the existing tested SR1 application |

The saved field names were verified after the forms returned to read-only mode. The billing-disabled flag was independently revealed and confirmed as `false`, then hidden again. Existing secret values were not inspected or changed. Latest deployment records did not change during these saves. Configuration is staged for the next deployment, not evidence that the running release uses it.

## Email and sandbox evidence

Auth0's Resend provider is saved and its provider, verification-template and reset-template test messages were delivered. See `SR1_EMAIL_SETUP.md` for the scope and limitations. Actual customer signup verification, reset-link completion and correct production return links remain acceptance checks.

Previously passed sandbox payment/access tests remain valid. No additional payment, subscription or customer was created for this checkpoint. No live payment is authorized or claimed.

## Live credential handoff

The connected Stripe tools remain authorized, but the cloud dashboard's Google-link flow returned a generic service error after a secure password submission. Account linking and dashboard login are unconfirmed. Stop repeated cloud login attempts. Credential values must stay in Stripe and Render settings, never in this repository or chat.

The owner can create a live restricted key named **SR1 Render Production** in their normal Stripe browser. Use these permissions and leave unrelated permissions at None:

| Resource | Permission |
| --- | --- |
| Prices | Read |
| Customers | Write |
| Checkout Sessions | Write |
| Subscriptions | Read |
| Invoices | Read |
| Customer/Billing Portal | Write |

Store it as `STRIPE_RESTRICTED_KEY` on the existing production backend with **Save only**. Use a live restricted key, not a sandbox key or unrestricted secret key. The assistant has not created, received or saved this live credential. The reviewed production webhook has not yet been registered and its signing secret is not yet configured.

## Remaining cutover

1. Supply the scoped live credential securely. Prepare the live webhook and securely save its signing secret; use the already tested event set and API version.
2. Preserve the production database and deliberately migrate legitimate legacy demo identities before disabling their login. The new startup backup is fail-closed, but a production migration/backup has not been run during this checkpoint.
3. Reconcile the legacy production Blueprint settings with the intended customer configuration before merging. In particular, legacy demo-login and demo-reassignment flags must not be reintroduced by Blueprint synchronization.
4. Apply the complete configuration with the reviewed release. Enable self-service trial access and retire legacy demo login only with the identity/data migration and new frontend. Activate approved live prices and billing only after credentials and webhook configuration are ready.
5. Verify production health, verified signup, saved work, real verification/reset link behavior, and checkout configuration. Do not charge a real card without separate authorization.
6. Connect the marketing Try/Create account/Login links only after the production journey is accepted. Keep the guided demo and SR2 design-partner paths.

This checkpoint is not a public launch. The release PR remains draft and unmerged.
