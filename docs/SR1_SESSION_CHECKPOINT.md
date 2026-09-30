# SR1 saved checkpoint — 30 September 2026, Athens

The owner requested that all completed work be saved. This checkpoint records verified progress through declined/successful sandbox payments, the corrected active-subscription display, saved edits after return login, the app-created customer portal, scheduled cancellation with retained project access, and the three-project Team limit.

## Saved locations

- Source, regression tests, Auth0 Action source, deployment Blueprint, and rollout documentation: branch `feature/sr1-trial-foundation`, draft [PR #1](https://github.com/JMSpanoman/fmea-ai/pull/1).
- Render: both isolated Docker services are live; the backend has its own persistent SQLite disk. The Stripe API key and webhook signing secret are stored in Render, outside source control.
- Auth0: SmartRisk 1 SPA, API, rotating refresh-token configuration, verified-email Action, email/password connection, and production/sandbox allowed origins are saved in the development tenant.
- Stripe sandbox: EUR monthly/yearly prices, customer portal configuration, and enabled signed webhook endpoint are saved. Live billing is disabled and the live catalog remains inactive.

Before the Check access correction, all 743 local source files matched their GitHub branch blob hashes, with no missing or extra source files. The sandbox backend is now on application commit `a5f50b5e3a8304b4cc71f7a9659991e9b016d9ab`, with the matching billing settings already applied through Render. The frontend-only Check access correction is saved in commit `baed3ba61721078e4ade627d6a5b5201fbc94dcd` and deployed to the sandbox. Render reports deployment `dep-dau4k8egekts73cuhsq0` live at 2026-09-29 23:31:39 UTC. Automatic deploys remain off.

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
| SR1 subscription display | Tester confirmed Subscription: active after the Check access correction at 2026-09-30 02:33 Athens; seat-limit acceptance remains pending |
| Saved work and return login | At 2026-09-30 02:37 Athens, tester confirmed a saved sample-project edit remained after sign-out and return login |
| App-created customer portal | Tester confirmed Manage subscription opens Stripe; backend POST `/billing/portal` returned 200 at 2026-09-29 23:36:57 UTC |
| Scheduled cancellation | Stripe reports active with `cancel_at=1793315323`, matching the current item period end: 2026-10-29 23:08:43 UTC / 30 October 01:08:43 Athens; `ended_at` is null |
| Cancellation update and retained access | Cancellation was requested at 23:37:29 UTC; a Stripe-origin webhook returned 200 at 23:37:31. The original sample project and its documents returned 200 at 23:40:22–23:40:23 UTC after the tester returned to SR1 |
| Team project limit | Tester confirmed the fourth project was blocked at 2026-09-30 02:45 Athens. Two additional POST `/projects` calls returned 201 at 23:44:33 and 23:44:50 UTC; the next returned 403 at 23:45:04 UTC, after the original sample project |
| Stripe webhook delivery | Three Stripe-origin webhook requests returned 200 at 23:08:46–23:08:47 UTC; no backend errors in this payment window |
| Webhook configuration | Enabled Stripe endpoint; signed synthetic probe/replay accepted, invalid signature and wrong-mode events rejected |
| Local regression checks | 21 backend and eight frontend tests passed; frontend build passed; baseline typecheck issues remain |

At the updated checkpoint, the Checkout Session is **complete and paid**, and Stripe confirms an **active** sandbox Team subscription. The failed charge was recorded at 2026-09-29 23:08:18 UTC and the successful charge at 23:08:43 UTC. The application's webhook accepted all three observed Stripe-origin requests. At 2026-09-30 02:33 Athens, the tester confirmed that the corrected Check access flow displays Subscription: active in SR1. At 02:37 Athens, the tester confirmed the saved sample edit remained after return login and the app-created Stripe portal opened. Stripe subsequently confirmed scheduled cancellation at the paid period end while the subscription remains active. SR1 accepted a Stripe-origin webhook during this change and served the same project afterward. The three-project Team limit has also passed: two new projects were created after the original sample, and the fourth attempt returned 403 with a limit message confirmed by the tester. Actual termination, failed renewal/recovery, and the five-seat limit still need acceptance. Stripe represents this portal cancellation with an explicit `cancel_at` timestamp equal to the item period end; `cancel_at_period_end` is false, so that boolean alone must not be used to conclude that cancellation is absent.

## Check access correction

The tester reported that Check access was visible but not clickable. Backend status requests were returning 200. The button shared the busy state used while opening Stripe, and a completed check had no visible feedback. The correction gives access checks a separate busy state, displays Checking access and a completion message, releases controls after navigation attempts, and refreshes status when Safari restores a cached billing page. Concurrent checks share one request; the account profile is refreshed only when its plan changes. Regression checks cover progress, unchanged and changed plans, the cached return, a pending Stripe action, and recovery after a failed status request. The sandbox frontend health and billing routes returned 200, and its served JavaScript contains the new progress/result messages and cached-return handler. The tester subsequently confirmed Subscription: active in their own browser.

## Production preparation — 30 September evening

- Rechecked the release: PR #1 is still draft and unmerged. Production has not received this release. Its previous deploy failed on the old database-migration import; the release branch already moves those migrations outside the disk mount and uses Python 3.11.
- Added a pre-schema SQLite snapshot for staging/production. Existing databases are backed up before `create_all` or runtime migrations. A SQLite integrity check and SHA-256 checksum verify the private snapshot on the persistent disk; backup failures stop startup before schema writes. Identical snapshots are reused; existing backups are never automatically deleted. This protects migration rollback; a separate off-service backup is still required for disaster recovery.
- The backup release was saved to GitHub and deployed to the sandbox backend. Render reports deployment `dep-daulsfrtqb8s73bspdtg` live at 2026-09-30 19:09:48 UTC. Startup verified a 1,843,200-byte SQLite snapshot on the persistent disk at 19:09:43 UTC before schema initialization, and application startup completed successfully.
- 21 backend checks passed, including backup retention of existing rows, corrupt-database failure, full app startup/restart, and rejecting startup when backup or migration fails. Eight frontend checks and the production frontend build remain at their previously verified results.
- Live Stripe account verification: Foton Consulting is a US company account with charges and payouts enabled, details submitted, and no currently-due or past-due account requirements. This does not establish its tax registrations.
- Live Stripe Tax was rechecked: settings are pending because the head-office address is missing, no default product tax code is set, and there are no active registrations. Do not infer tax jurisdiction from personal residence or enable automatic tax without the business's confirmed setup.
- The connected Stripe tool supports subscription updates but does not expose payment-method attachment, invoice payment, or advancing a test clock. No simulation clock or billing mutation was created. Remaining deployed failure/recovery tests need Dashboard or authenticated CLI access.
- The available cloud Stripe tab is at its sign-in page and SR1 is awaiting sign-in to the existing sandbox account; the prior signed-in tabs are not present. Render and Stripe connectors continue to work. No passwords or API secrets were requested in chat. Auth0 CLI authentication is not available in this execution session.
- Website routes were checked: Try SR1 goes through request-access pages to the contact form; the public login still targets the existing production workspace. The new trial journey has not been published there.

## Owner confirmation and website update — 30 September, 22:55 Athens

- The owner confirmed Foton's business is in the United States and currently has no VAT or sales-tax registrations. This records current registration status; it is not a determination of where registration or collection is required. No registration, exemption, product tax code, or head-office street address was invented or added. Automatic Tax remains disabled.
- The owner confirmed the team-seat test has not been run. Four pending invitations plus the owner must exhaust the five-seat allowance. Revoking one pending invitation must free a seat. Invitation creation only produces a copyable link; the application sends no invitation email.
- Marketing website version 18 was published successfully at https://www.fotonconsulting.com from Site source commit `1a1de3f01f91750dd1324b33a5436553cf170852`. The existing SR1 and trial pages now clarify EUR 399/month or EUR 3,990/year excluding VAT, five users including the owner, three shared projects in total, the sample project's use of a project slot, saved-work continuity, automatic renewal, and cancellation terms. The misleading Team "by quote" label was removed; implementation/enterprise options remain separate discussions.
- The website build passed and existing page routes remain in the build. Public access requests, guided demos, and SR2 design-partner positioning are unchanged. Production self-service signup and live checkout are still not connected.
- Production email setup, secure production billing credentials, and the remaining deployed account/billing acceptance checks remain outstanding. The cloud SR1 sign-in attempt was interrupted; the tester's own-browser login does not provide an assistant session.

## Next acceptance steps

1. Verify the five-seat limit, invitation acceptance/removal and shared project access, repeated-click protection, and Checkout cancellation. The three-project owner limit has passed; members must also share that quota. Saved edits across sign-out/return login, the app-created portal, scheduled subscription cancellation, and immediate retention of project access have passed.
2. Test actual subscription termination, failed renewal and recovery, trial expiry, and direct API access restrictions while retaining saved work. The initial card decline followed by successful payment is already verified; it does not replace a failed-renewal test.
3. Confirm production email delivery setup, supply production credentials securely, and complete production readiness before merging or enabling live payments. The owner has confirmed US business location and no current tax registrations; only configure tax collection for confirmed applicable registrations. The startup backup must protect the existing database before migration.
4. Verify the public marketing site's Try/Create account/plan links against the approved production journey before launch.

## Practical notes

- Sandbox signup: https://sr1-sandbox-frontend-dczh.onrender.com/create-account
- Sandbox plans: https://sr1-sandbox-frontend-dczh.onrender.com/billing
- The tester uses their own browser. Its login session does not transfer to the assistant; passwords and codes must not be shared in chat.
- The initial Checkout blocker was insufficient restricted-key permissions. Required permissions and the resolution are recorded in `SR1_TRIAL_ROLLOUT.md`. The Stripe connector cannot edit API-key permissions.
- The sandbox AI-generation key is not configured. Sample-project and billing tests do not require it.
- VAT-exclusive prices are configured; automatic tax calculation remains off. The owner reports a US business with no current VAT or sales-tax registrations. Do not represent this as a tax exemption or invent registrations.
- The previously exposed sandbox secret key's rotation has not been confirmed. Verify that it has been rotated or revoked before further use; the app uses a separate restricted key.
- The draft is saved and deployed for testing. It is not a completed live launch.
