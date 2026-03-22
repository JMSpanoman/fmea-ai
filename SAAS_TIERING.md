# SmartRisk SaaS Tiering Architecture

## Overview

SmartRisk supports two product tiers:

- **SmartRisk Lite** (default for new users): AI-generated FMEA, editable FMEA table, live RPN calculation, CSV export
- **SmartRisk Pro**: All features including projects, version control, traceability, design controls, CAPA, etc.

## Architecture

### Database

- **User model** (`fmea_backend/models/user.py`): `plan` column with values `"lite"` | `"pro"`, default `"lite"`
- **Runtime migration** (`fmea_backend/db/runtime_migrations.py`): `ensure_user_columns()` adds `plan` to existing users

### Backend Feature Gating

- **Plan dependency** (`fmea_backend/auth/plan.py`):
  - `get_user_plan(user)` – resolve plan, default to lite
  - `require_pro` – FastAPI dependency, raises 403 if not Pro
  - `is_pro(user)` – helper boolean

- **Pro-only routers** use `dependencies=[Depends(require_pro)]` on the APIRouter:
  - `projects`, `components`, `fmea`, `export`, `document_control`, `document_guidance`
  - `traceability`, `traceability_impact`, `hazard_analysis`, `risk_items`
  - `design_controls`, `vv`, `capa_phase2`, `pms`, `pms_signal`
  - `risk_management_plan`, `rmf`, `residual_risk`, `risk_controls_doc`
  - `reports_*`, `project_profile`, `project_initialize`
  - Phase 3: `training`, `audit`, `supplier`, `ncr`, `complaint`, `equipment`, `quality_event`, `change_control`, `approval`
  - AI: `ai_phase2`, `ai_phase3`

- **Lite-accessible**:
  - `auth` (login, me, dev-login)
  - Legacy `ai` (`/fmea/fmea/generate`, `/fmea/pfmea/generate`) – AI FMEA generation
  - `ai_phase1` (`/ai/fmea/suggest`, `/ai/fmea/check`) – AI suggestions

### Loading Pro in local development

- **Dev login** (`POST /auth/dev-login`): In non–production-like environments (`ENVIRONMENT` not `production` / `prod` / `staging`), the resolved plan defaults to **Pro** and the user row is updated accordingly.
- **Auth0 users**: New users are created with plan **lite** in the database. In **non–production-like** environments, the API **defaults** to treating every user as **Pro** (`SMARTRISK_DEV_FORCE_PRO` defaults to enabled). Opt out with **`SMARTRISK_DEV_FORCE_PRO=false`** if you need to test Lite locally.
- **Manual override**: `UPDATE users SET plan = 'pro' WHERE email = 'you@example.com';`
- **Staging / production**: `SMARTRISK_DEV_FORCE_PRO` is ignored; plan should come from subscription/admin tooling (future) or manual DB updates.

### Frontend Feature Flags

- **Config** (`frontend/src/config/features.ts`):
  - `featuresByPlan`, `getFeatures(plan)`, `isProPlan(plan)`
  - `FeatureFlags` interface and `NavItemConfig` with `requiresPro`

- **Auth** (`frontend/src/contexts/AuthContext.tsx`): User type includes `plan`; `/auth/me` returns it

- **AppShell** (`frontend/src/components/layout/AppShell.tsx`):
  - Filters nav items by `requiresPro` for Lite users
  - Shows "Lite" badge for non-Pro

- **LandingPage**: Lite users → `/dfmea`; Pro users → project flow

- **ProRoute** (`frontend/src/components/ProRoute.tsx`): Wraps `/projects/*` routes; redirects Lite users to `/dfmea`

- **ProGate** (`frontend/src/components/ProGate.tsx`): Renders upgrade message or redirects Lite users

- **403 handler** (`frontend/src/axios.ts`): Emits `api:403:pro` custom event when backend returns Pro-gate 403

### Folder Structure

```
fmea_backend/
├── auth/
│   ├── dependencies.py   # get_current_user, ensures plan on user
│   └── plan.py           # require_pro, get_user_plan, is_pro
├── models/
│   └── user.py           # plan column, PLAN_LITE, PLAN_PRO
├── db/
│   └── runtime_migrations.py  # ensure_user_columns
└── routers/              # Pro routers have dependencies=[Depends(require_pro)]

frontend/
├── src/
│   ├── config/
│   │   └── features.ts   # featuresByPlan, getFeatures, isProPlan
│   ├── contexts/
│   │   └── AuthContext.tsx  # user.plan
│   ├── components/
│   │   ├── ProGate.tsx   # Upgrade CTA for Lite
│   │   ├── ProRoute.tsx  # Wrapper for Pro routes
│   │   └── Api403ProListener.tsx  # Toast on 403 Pro
│   └── pages/
│       ├── LandingPage.tsx  # Lite → /dfmea, Pro → projects
│       └── FMEAPage.tsx     # Lite mode: no projects, no MasterControl
```

## Future Extensions

### Stripe Integration

- Add `stripe_customer_id`, `stripe_subscription_id` to User
- Webhook handler to sync subscription status → `user.plan`
- Keep `require_pro` and `getFeatures` unchanged; plan source becomes Stripe

### Auth0 Integration

- Auth0 returns user metadata; map `app_metadata.plan` or custom claim to `user.plan`
- Ensure `/auth/me` and dev-login both return `plan`

### Additional Tiers (starter, enterprise)

- Add `PLAN_STARTER`, `PLAN_ENTERPRISE` to models
- Extend `featuresByPlan` and `FeatureFlags`
- Add `require_enterprise` or plan hierarchy helpers in `auth/plan.py`
