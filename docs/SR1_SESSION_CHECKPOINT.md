# SR1 saved checkpoint — 30 September 2026, Athens

The owner requested that all completed work be saved. This checkpoint records verified progress without treating an open Checkout Session as a completed payment.

## Saved locations

- Source, regression tests, Auth0 Action source, deployment Blueprint, and rollout documentation: branch `feature/sr1-trial-foundation`, draft [PR #1](https://github.com/JMSpanoman/fmea-ai/pull/1).
- Render: both isolated Docker services are live; the backend has its own persistent SQLite disk. The Stripe API key and webhook signing secret are stored in Render, outside source control.
- Auth0: SmartRisk 1 SPA, API, rotating refresh-token configuration, verified-email Action, email/password connection, and production/sandbox allowed origins are saved in the development tenant.
- Stripe sandbox: EUR monthly/yearly prices, customer portal configuration, and enabled signed webhook endpoint are saved. Live billing is disabled and the live catalog remains inactive.

Before adding this documentation checkpoint, all 742 local source files matched their GitHub branch blob hashes, with no missing or extra source files. Both running services use application commit `c5021e2`; later commits contain deployment configuration and documentation updates, with the matching billing settings already applied through Render.

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
| Webhook configuration | Enabled Stripe endpoint; signed synthetic probe/replay accepted, invalid signature and wrong-mode events rejected |
| Local regression checks | 19 backend and five frontend tests passed; frontend build passed; baseline typecheck issues remain |

The latest observed Checkout Session is **open and unpaid**, with no subscription created. Actual Stripe payment-event delivery and resulting paid access are not yet verified. The screenshot is proof of reaching Checkout, not proof of payment.

## Next acceptance steps

1. In the already-open sandbox Checkout, select Card and disable optional Link information saving. Test a decline with Stripe test card `4000 0000 0000 9995`, then a successful payment with `4242 4242 4242 4242`. Use a future expiry and any three-digit CVC. Use test cards only. Reference: https://docs.stripe.com/testing.
2. Verify the Stripe payment/subscription, 2xx delivery of actual Stripe events, SR1's active Team state, and continued access to the same saved project. Do not grant access based on the success redirect alone.
3. Verify edited-row persistence across reload and sign-out/return login, three-project and five-seat limits, repeated-click protection, Checkout cancellation, and the app-created billing portal.
4. Test cancellation at period end and actual termination, failed renewal and recovery, trial expiry, and direct API access restrictions while retaining saved work.
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
