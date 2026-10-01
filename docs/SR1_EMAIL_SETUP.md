# SR1 transactional email setup

Status: Auth0 is connected to Resend. Provider, verification-template and password-reset-template tests were delivered on 1 October 2026 between 01:39 and 01:48 Europe/Athens. Actual customer signup/reset link completion through the new provider remains a production acceptance step.

## Configured

- Provider account: Resend `fotonconsulting`.
- Sending domain: `notify.fotonconsulting.com`.
- Region: North Virginia (`us-east-1`).
- Sending enabled, receiving disabled. Click tracking and open tracking are both disabled, confirmed through the Resend connector.
- Authoritative DNS is managed by Wix (`ns0.wixdns.net`, `ns1.wixdns.net`).

The following exact provider-issued records were added with TTL 3600 using an additions-only update. All original DNS records were preserved; no root mail routing, SPF, website records or DNSSEC settings were changed.

| Type | Host | Value |
| --- | --- | --- |
| TXT | `resend._domainkey.notify.fotonconsulting.com` | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC9AXcCynAiC8W4pUAOmKNd2BSbpja687DFuhkroewI+CXVve9gCO/rslVQcYrUWU2Pf7EQuGREnd3lDt6Pev5Nph+3Tc85cpQi38K6H2857x4LIvRkuf0+6f7P5nerP3Sh5wapT8z2aFyttuvUVncb//F+ohTShxDBFECJTjjJ7wIDAQAB` |
| CNAME | `rsend.notify.fotonconsulting.com` | `rsend.forge.rmta.net` |
| CNAME | `send.notify.fotonconsulting.com` | `send.forge.rmta.net` |

The DKIM value above is a public verification key, not an API secret. No root DMARC policy was added or changed. Resend's domain page reports Verified. Separate delivery evidence is recorded below.

## Auth0 provider configured

- Reused the existing Auth0 tenant and confirmed administrator access.
- Branding → Email Provider: **Use my own email provider** enabled, **Resend** selected and saved.
- From: `SmartRisk <accounts@notify.fotonconsulting.com>`.
- Permission: **Sending access**, limited to `notify.fotonconsulting.com`.
- Following the owner's specific approval, a scoped sending credential was transferred directly into Auth0 and saved there. Credential values and metadata are omitted from this document. Temporary browser clipboards were cleared.
- Verification Email (Link) and Change Password (Link) templates are enabled. Default templates remain unchanged and inherit the provider sender. No Reply-To was configured; the provider form has no Reply-To field.

## Delivery verification

The owner approved setup messages to an owner-controlled business mailbox. Resend reports all three **delivered**:

| Test | Result |
| --- | --- |
| Email Provider Configuration Test | Delivered |
| Verify your email — template Try test | Delivered |
| Reset your password — template Try test | Delivered |

Delivered means the receiving mail server accepted each message. It does not prove inbox reading or completion of a verification/reset link. The approved recipient is the Auth0 administrator and has no SR1 customer identity in this tenant. Consequently these are Auth0 template tests, not a new customer signup or a real customer's password reset. No customer passwords or identities were changed.

## Remaining launch checks

1. During production acceptance, complete signup verification and password reset from SR1 using an owner-controlled customer account. Confirm delivery and correct application return links. Password creation/reset entry remains with the user. Retain the existing verified-email requirement.
2. Complete the separately documented live Stripe restricted key, webhook secret and production runtime configuration; deploy the reviewed release with its verified database backup.
3. Verify the production journey before activating public trial/signup links. Email-provider delivery alone does not complete the live product launch.

Official integration instructions: https://auth0.com/docs/customize/email/smtp-email-providers/resend
