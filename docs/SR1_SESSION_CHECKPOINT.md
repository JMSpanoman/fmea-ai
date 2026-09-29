# SR1 saved checkpoint — 30 September 2026, Athens

The owner requested that all completed work be saved. This checkpoint records verified progress, updated after the tester completed the declined and successful sandbox payment cases and reported an unresponsive Check access button.

## Saved locations

- Source, regression tests, Auth0 Action source, deployment Blueprint, and rollout documentation: branch `feature/sr1-trial-foundation`, draft [PR #1](https://github.com/JMSpanoman/fmea-ai/pull/1).
- Render: both isolated Docker services are live; the backend has its own persistent SQLite disk. The Stripe API key and webhook signing secret are stored in Render, outside source control.
- Auth0: SmartRisk 1 SPA, API, rotating refresh-token configuration, verified-email Action, email/password connection, and production/sandbox allowed origins are saved in the development tenant.
- Stripe sandbox: EUR monthly/yearly prices, customer portal configuration, and enabled signed webhook endpoint are saved. Live billing is disabled and the live catalog remains inactive.

Before the Check access correction, all 743 local source files matched their GitHub branch blob hashes, with no missing or extra source files. The backend remains on application commit `c5021e2`, with the matching billing settings already applied through Render. This checkpoint includes a frontend-only billing-page correction, to be deployed explicitly to the sandbox because automatic deploys are off.

## Current offer

- Trial: 14 days, no card, one user and one project.
- Team: EUR 399/month or EUR 3,990/year, excluding VAT; five users including the owner and three shared projects.
- Guided pilot: sales-led, 30 days, by quote.
- Saved work is retained after trial expiry or cancellation; access follows the verified account and current billing status.

## Verified in the deployed sandbox

| Check | Evidence/result |
|---|---|
| Deployment | Both services live; health endpoints returned 200 |
| Signup and verified login | Fresh Auth0 identity verified; signed-token `/auth/me` returned 200 |
| Trial | App screenshot displays the 14-day trial and its end date |
| Sample project | `/projects/sample` returned 201; saved sample FMEA retrieved with 200 |
| Plan comparison | App displays the approved EUR prices, limits, renewal, cancellation, and VAT wording |
| Monthly Checkout | App endpoint returned 200; Stripe session is sandbox, EUR 399, subscription mode |
| Declined payment | Stripe recorded an issuer decline with insufficient funds for EUR 399 |
| Successful payment | The same PaymentIntent then succeeded for EUR 399; Checkout is complete and paid |
| Subscription | Stripe confirms an active sandbox subscription, one unit of the approved monthly price, linked to the app account |
| Stripe webhook delivery | Three Stripe-origin webhook requests returned 200 at 23:08:46–23:08:47 UTC; no backend errors in this payment window |
| Webhook configuration | Enabled Stripe endpoint; signed synthetic probe/replay accepted, invalid signature and wrong-mode events rejected |
| Local regression checks | 19 backend and eight frontend tests passed; frontend build passed; baseline typecheck issues remain |

At the updated checkpoint, the Checkout Session is **complete and paid**, and Stripe confirms an **active** sandbox Team subscription. The failed charge was recorded at 2026-09-29 23:08:18 UTC and the successful charge at 23:08:43 UTC. The application's webhook accepted all three observed Stripe-origin requests. The tester still needs to confirm that the SR1 UI displays active Team access and that saved work remains available. Successful webhook delivery alone is not direct observation of the account's resulting application permissions.

## Check access correction

The tester reported that Check access was visible but not clickable. Backend status requests were returning 200. The button shared the busy state used while opening Stripe, and a completed check had no visible feedback. The correction gives access checks a separate busy state, displays Checking access and a completion message, releases controls after navigation attempts, and refreshes status when Safari restores a cached billing page. Concurrent checks share one request; the account profile is refreshed only when its plan changes. Regression checks cover progress, unchanged and changed plans, the cached return, a pending Stripe action, and recovery after a failed status request. The tester's browser confirmation remains pending after deployment.

## Next acceptance steps

1. In SR1 plans, select Check access and confirm that the Team subscription is active. Open the same sample project and confirm the previously saved edit remains. Stripe payment/subscription and 2xx webhook delivery have been verified; application access still needs the tester's observation. Do not grant access based on the success redirect alone.
2. Open Manage subscription through SR1, verify the customer portal, and test cancellation at the end of the paid period. Confirm the scheduled cancellation in Stripe and retained app access until that period ends.
3. Verify edited-row persistence across reload and sign-out/return login, three-project and five-seat limits, repeated-click protection, Checkout cancellation, and the app-created billing portal.
4. Test actual subscription termination, failed renewal and recovery, trial expiry, and direct API access restrictions while retaining saved work. The initial card decline followed by successful payment is already verified; it does not replace a failed-renewal test.
5. Confirm production email delivery setup and tax treatment/registrations, supply production credentials securely, back up the existing database, and complete production readiness before merging or enabling live payments.
6. Verify the public marketing site's Try/Create account/plan links against the approved production journey before launch.

## Practical notes

- Sandbox signup: https://sr1-sandbox-frontend-dczh.onrender.com/create-account
- Sandbox plans: https://sr1-sandbox-frontend-dczh.onrender.com/billing
- The tester uses their own browser. Its login session does not transfer to the assistant; passwords and codes must not be shared in chat.
- The initial Checkout blocker was insufficient restricted-key permissions. Required permissions and the resolution are recorded in `SR1_TRIAL_ROLLOUT.md`. The Stripe connector cannot edit API-key permissions.
- The sandbox AI-generation key is not configured. Sample-project and billing tests do not require it.
- VAT-exclusive prices are configured; automatic VAT calculation remains off. Confirm the legal entity's tax setup before live activation.
- The previously exposed sandbox secret key's rotation has not been confirmed. Verify that it has been rotated or revoked before further use; the app uses a separate restricted key.
- The draft is saved and deployed for testing. It is not a completed live launch.
