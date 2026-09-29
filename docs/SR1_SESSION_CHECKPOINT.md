# SR1 saved checkpoint — 30 September 2026, Athens

The owner requested that all completed work be saved. This checkpoint records verified progress through declined/successful sandbox payments, the corrected active-subscription display, saved edits after return login, the app-created customer portal, and scheduled cancellation with retained project access.

## Saved locations

- Source, regression tests, Auth0 Action source, deployment Blueprint, and rollout documentation: branch `feature/sr1-trial-foundation`, draft [PR #1](https://github.com/JMSpanoman/fmea-ai/pull/1).
- Render: both isolated Docker services are live; the backend has its own persistent SQLite disk. The Stripe API key and webhook signing secret are stored in Render, outside source control.
- Auth0: SmartRisk 1 SPA, API, rotating refresh-token configuration, verified-email Action, email/password connection, and production/sandbox allowed origins are saved in the development tenant.
- Stripe sandbox: EUR monthly/yearly prices, customer portal configuration, and enabled signed webhook endpoint are saved. Live billing is disabled and the live catalog remains inactive.

Before the Check access correction, all 743 local source files matched their GitHub branch blob hashes, with no missing or extra source files. The backend remains on application commit `c5021e2`, with the matching billing settings already applied through Render. The frontend-only Check access correction is saved in commit `baed3ba61721078e4ade627d6a5b5201fbc94dcd` and deployed to the sandbox. Render reports deployment `dep-dau4k8egekts73cuhsq0` live at 2026-09-29 23:31:39 UTC. Automatic deploys remain off.

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
| SR1 subscription display | Tester confirmed Subscription: active after the Check access correction at 2026-09-30 02:33 Athens; paid-limit acceptance remains pending |
| Saved work and return login | At 2026-09-30 02:37 Athens, tester confirmed a saved sample-project edit remained after sign-out and return login |
| App-created customer portal | Tester confirmed Manage subscription opens Stripe; backend POST `/billing/portal` returned 200 at 2026-09-29 23:36:57 UTC |
| Scheduled cancellation | Stripe reports active with `cancel_at=1793315323`, matching the current item period end: 2026-10-29 23:08:43 UTC / 30 October 01:08:43 Athens; `ended_at` is null |
| Cancellation update and retained access | Cancellation was requested at 23:37:29 UTC; a Stripe-origin webhook returned 200 at 23:37:31. The original sample project and its documents returned 200 at 23:40:22–23:40:23 UTC after the tester returned to SR1 |
| Stripe webhook delivery | Three Stripe-origin webhook requests returned 200 at 23:08:46–23:08:47 UTC; no backend errors in this payment window |
| Webhook configuration | Enabled Stripe endpoint; signed synthetic probe/replay accepted, invalid signature and wrong-mode events rejected |
| Local regression checks | 19 backend and eight frontend tests passed; frontend build passed; baseline typecheck issues remain |

At the updated checkpoint, the Checkout Session is **complete and paid**, and Stripe confirms an **active** sandbox Team subscription. The failed charge was recorded at 2026-09-29 23:08:18 UTC and the successful charge at 23:08:43 UTC. The application's webhook accepted all three observed Stripe-origin requests. At 2026-09-30 02:33 Athens, the tester confirmed that the corrected Check access flow displays Subscription: active in SR1. At 02:37 Athens, the tester confirmed the saved sample edit remained after return login and the app-created Stripe portal opened. Stripe subsequently confirmed scheduled cancellation at the paid period end while the subscription remains active. SR1 accepted a Stripe-origin webhook during this change and served the same project afterward. Actual termination, failed renewal/recovery, and paid project/seat limits still need acceptance. Stripe represents this portal cancellation with an explicit `cancel_at` timestamp equal to the item period end; `cancel_at_period_end` is false, so that boolean alone must not be used to conclude that cancellation is absent.

## Check access correction

The tester reported that Check access was visible but not clickable. Backend status requests were returning 200. The button shared the busy state used while opening Stripe, and a completed check had no visible feedback. The correction gives access checks a separate busy state, displays Checking access and a completion message, releases controls after navigation attempts, and refreshes status when Safari restores a cached billing page. Concurrent checks share one request; the account profile is refreshed only when its plan changes. Regression checks cover progress, unchanged and changed plans, the cached return, a pending Stripe action, and recovery after a failed status request. The sandbox frontend health and billing routes returned 200, and its served JavaScript contains the new progress/result messages and cached-return handler. The tester subsequently confirmed Subscription: active in their own browser.

## Next acceptance steps

1. Verify three-project and five-seat limits, repeated-click protection, and Checkout cancellation. Saved edits across sign-out/return login, the app-created portal, scheduled subscription cancellation, and immediate retention of project access have passed.
2. Test actual subscription termination, failed renewal and recovery, trial expiry, and direct API access restrictions while retaining saved work. The initial card decline followed by successful payment is already verified; it does not replace a failed-renewal test.
3. Confirm production email delivery setup and tax treatment/registrations, supply production credentials securely, back up the existing database, and complete production readiness before merging or enabling live payments.
4. Verify the public marketing site's Try/Create account/plan links against the approved production journey before launch.

## Practical notes

- Sandbox signup: https://sr1-sandbox-frontend-dczh.onrender.com/create-account
- Sandbox plans: https://sr1-sandbox-frontend-dczh.onrender.com/billing
- The tester uses their own browser. Its login session does not transfer to the assistant; passwords and codes must not be shared in chat.
- The initial Checkout blocker was insufficient restricted-key permissions. Required permissions and the resolution are recorded in `SR1_TRIAL_ROLLOUT.md`. The Stripe connector cannot edit API-key permissions.
- The sandbox AI-generation key is not configured. Sample-project and billing tests do not require it.
- VAT-exclusive prices are configured; automatic VAT calculation remains off. Confirm the legal entity's tax setup before live activation.
- The previously exposed sandbox secret key's rotation has not been confirmed. Verify that it has been rotated or revoked before further use; the app uses a separate restricted key.
- The draft is saved and deployed for testing. It is not a completed live launch.
