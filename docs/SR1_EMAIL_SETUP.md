# SR1 transactional email setup

Status: Resend sending domain verified on 1 October 2026 at 01:19 Europe/Athens. Auth0 integration and actual email delivery are not yet complete.

## Configured

- Provider account: Resend `fotonconsulting`.
- Sending domain: `notify.fotonconsulting.com`.
- Resend domain ID: `23e3d4b7-4a5e-4c59-b4bf-1b16d034a84d`.
- Region: North Virginia (`us-east-1`).
- Sending enabled, receiving disabled, tracking not configured.
- Authoritative DNS is managed by Wix (`ns0.wixdns.net`, `ns1.wixdns.net`).

The following exact provider-issued records were added with TTL 3600 using an additions-only update. All original DNS records were preserved; no root mail routing, SPF, website records or DNSSEC settings were changed.

| Type | Host | Value |
| --- | --- | --- |
| TXT | `resend._domainkey.notify.fotonconsulting.com` | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC9AXcCynAiC8W4pUAOmKNd2BSbpja687DFuhkroewI+CXVve9gCO/rslVQcYrUWU2Pf7EQuGREnd3lDt6Pev5Nph+3Tc85cpQi38K6H2857x4LIvRkuf0+6f7P5nerP3Sh5wapT8z2aFyttuvUVncb//F+ohTShxDBFECJTjjJ7wIDAQAB` |
| CNAME | `rsend.notify.fotonconsulting.com` | `rsend.forge.rmta.net` |
| CNAME | `send.notify.fotonconsulting.com` | `send.forge.rmta.net` |

The DKIM value above is a public verification key, not an API secret. No root DMARC policy was added or changed. Resend's domain page reports Verified; this is provider verification, not evidence that any email has been sent.

## Prepared, not submitted

The Resend API-key form is ready with:

- Name: `SR1 Auth0 transactional email`.
- Permission: `Sending access`.
- Domain: `notify.fotonconsulting.com` only.

No key was created. Browser creation of a persistent credential requires action-time approval; keep its value out of chat, repository files, screenshots and command logs. Ensure the Auth0 destination is accessible before creating a one-time-visible key.

## Remaining integration

1. Reuse the existing Auth0 tenant `dev-h8xzqvip220o54ml.us.auth0.com`; do not create a replacement tenant or authentication system. The administrator login email has not been established.
2. Configure Branding → Email Provider → Resend with the scoped sending key. Proposed From identity: `SmartRisk <accounts@notify.fotonconsulting.com>`. This setting is not yet saved. Where supported, use the monitored `john@fotonconsulting.com` as Reply-To/support contact.
3. Save the provider settings and verify actual delivery of a provider test, a signup-verification email and a password-reset email with an owner-controlled account. Obtain explicit authorization for any assistant-triggered message. Password choice/reset entry remains with the user.
4. Inspect delivery in Resend and Auth0, verify links return to the correct SR1 environment, and retain the existing verified-email requirement.
5. Continue the separately documented live Stripe credentials/webhook and production rollout. Do not activate public trial links or live checkout solely because the sending domain is verified.

Official integration instructions: https://auth0.com/docs/customize/email/smtp-email-providers/resend
