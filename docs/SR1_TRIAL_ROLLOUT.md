# SR1 14-day trial foundation (draft)

This change is **not a public signup launch**. It adds server-side trial dates and a one-project limit for newly verified Auth0 identities. Existing demo users and their plan remain unchanged. No billing or checkout is included.

## Before enabling on Render

1. Configure a real Auth0 application and API audience for `fmea-frontend-dczh` and `fmea-backend-dczh`. Implement and test the frontend Auth0 sign-in route; the current frontend uses `/auth/dev-login` and cannot serve public accounts safely.
2. Apply `fmea_backend/migrations/add_user_trial_dates.sql` if the backend is using PostgreSQL. The current Render blueprint declares SQLite, which uses an idempotent startup migration.
3. Verify that the persistent Render database disk is retained and backed up; the blueprint references `sqlite:////app/db/fmea.db` but does not itself declare a disk.
4. Only after verified Auth0 sign-in works, set `ENABLE_SELF_SERVICE_TRIALS=true` on the backend. New verified Auth0 users then receive 14 days. Existing users are not retroactively enrolled.
5. Disable the production email-only dev login once the authorized demo users have a replacement sign-in. It currently creates a session from an allowlisted email without proving ownership.
   When `ENABLE_SELF_SERVICE_TRIALS=true`, the server now rejects `/auth/dev-login` even if the old `ALLOW_DEV_LOGIN=true` Render setting remains. Migrate the two demo accounts before enabling trials. Auth0 users never inherit the email-based demo admin override.
6. Add organization/team membership, five-seat and three-project paid limits, and Stripe Checkout, signed webhooks, subscription status, and billing portal before accepting payments. Never grant `plan=pro` based solely on a checkout redirect.
7. Exercise signup, exact expiry boundary, first/second project, paid activation, payment failure, cancellation, existing demo identity, and login after logout in an isolated environment before changing the marketing CTA.

Approved offer: 14 days, one user and one project, no card; Team €399/month or €3,990/year with five users and three active projects; a separate 30-day guided pilot by quote. Public checkout remains disabled until the paid entitlement path is verified.
