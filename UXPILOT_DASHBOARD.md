# SmartQS — Dashboard UX Spec (for uxpilot.ai)

Use this file as the **single source of truth** to generate a “Dashboard” experience in uxpilot.ai that matches the current SmartQS UI implementation.

## Product Context

SmartQS (Smart Quality System) is a QMS/Risk-management workspace. Users manage Projects and project documents (Risk Management, Design Controls, V&V, Traceability, etc.).

## App Shell (global layout)

- **Layout**: Left sidebar + top bar + main content area.
- **Sidebar**
  - Default: **collapsed** (narrow icons-only).
  - Expanded width: ~320px; collapsed width: ~72px.
  - Sections:
    - **Project**: Dashboard, Projects, Documents, Traceability, Export, History (placeholder)
    - **Documentation**: dynamic document groups (from registry), each navigates to `/projects/:projectId/docs/:groupId`
  - “Dashboard” behavior:
    - Sidebar item “Dashboard” navigates to **project dashboard** if a project is selected: `/projects/:projectId/dashboard`
    - Otherwise: navigates to `/` (global dashboard)
- **Top bar**
  - Shows current project name (when selected) and “Switch Project” (placeholder).
  - Command bar trigger: `⌘K Jump`
  - “✨ AI Assistant” toggle (panel slides in/out)
  - User menu (avatar with first 2 letters of email) with Sign Out

## Screen 1 — Global Dashboard

- **Route(s)**: `/` and `/dashboard`
- **Title**: “Dashboard”
- **Subtitle**: “Overview of your quality management activities”

### Primary layout

1) **Metrics row (4 cards)**
- Card style: white surface, subtle hover.
- Each card contains:
  - Left icon (emoji)
  - Right badge (change indicator)
  - Big metric value + label
- Metrics (current hardcoded values):
  - “Total Open Risks” = 12, badge “+3”, variant danger, icon 🛡️
  - “High RPN Count” = 8, badge “+2”, variant danger, icon ⚠️
  - “Open CAPAs” = 8, badge “4 due soon”, variant info, icon 🔧
  - “Open Changes” = 7, badge “3 today”, variant success, icon 🔄

2) **Main grid**
- Two-column + one-column layout on large screens:
  - **Risk Trends** (wide card)
    - Contains 3 rows with a label + progress bar + badge score
    - Example rows:
      - Power Management IC — progress 85% — badge 85 (danger)
      - Battery Life Sensor — progress 72% — badge 72 (warning)
      - Signal Processing Unit — progress 64% — badge 64 (info)
  - **AI Insights** (side card)
    - Title: “✨ AI Insights”
    - List of 3 insight cards (static text)
    - Button: “View All Insights” (primary, full width)

3) **Recent Projects**
- Card title: “Recent Projects”
- Top-right button: “View All” → navigates to `/projects`
- Content states:
  - Loading: “Loading projects…”
  - Empty: “No projects found”
  - Loaded:
    - Grid of up to 6 projects (cards)
    - Each project card:
      - Title = project.name
      - Status badge: “Active”
      - Optional description (2-line clamp)
      - Footer: created date + ghost button “View →”
      - Click behavior: navigate to `/dfmea?project={project.id}`

### UX rules

- Global dashboard should feel like an **overview**; metrics may be placeholders until real data exists.
- Keep interactions safe: no destructive actions, no auto-approvals.

## Screen 2 — Project Dashboard (“Mission Control”)

- **Route**: `/projects/:projectId/dashboard`
- **Header**: “Mission Control”
- **Project identity line**: `Project: {projectName} ({projectId})`

### Header actions (top right)

- **Reload**: reloads documents list (shows “Loading…” when active)
- **Project Docs**: `/projects/:projectId/documents`
- **Documentation**: `/projects/:projectId/docs`

### System banners / states (top-of-page)

Show in this order when applicable:

1) **Action failed** (red)
- Triggered by user actions failing (initialize drafts, AI FMEA, etc.)

2) **Action result** (blue)
- Only for explicit user-triggered deterministic draft generation (not for silent AI FMEA)

3) **Initial drafts generated from project setup** (green)
- Appears when key docs include deterministic marker text
- Explains: created deterministically from Project Profile + Components

4) **Generate initial drafts CTA** (sky)
- Appears when project setup exists but key docs are empty/starter
- Primary button: “Generate initial drafts” → POST `/projects/:projectId/initialize-from-profile`

5) **Setup incomplete** (amber)
- Appears when setup is missing required info (intended use + at least 1 component)
- Primary button: “Complete setup” → `/projects/:projectId/setup`

6) **Load error** (red)
- Shows retry button “Retry”

### Main content blocks

1) **Next Actions** (full width)
- Auto-generated checklist based on missing required artifacts and stale drafts.
- Required types:
  - rmp, hazard_analysis, fmea, risk_controls_doc, residual_risk, rmf, traceability_matrix
- If a required doc is not started → action “Create”
- If a draft is stale (>30 days) → action “Continue”
- If traceability matrix not approved → action uses status-based CTA label
- Each action navigates to the relevant document page.

2) **Key widgets grid (3 columns on xl)**
- **Project Readiness**
  - Overall % derived from approval status
  - Category breakdown bars:
    - Risk Management (rmp, hazard_analysis, fmea, risk_controls_doc, residual_risk, rmf)
    - Design Controls (design_inputs_doc, design_outputs_doc)
    - V&V (vv_evidence)
    - Traceability (traceability_matrix)
- **Traceability Health**
  - Honest placeholder: linked/missing/broken remain “Unknown” until telemetry exists
- **High Risk Items**
  - Placeholder “Unknown” with explanatory copy

3) **Hotspots + Recent Activity (2 columns on xl)**
- **Risk Hotspots**
- **Recent Activity**

4) **Documents Hub**
- Grouped cards:
  - Risk Management (rmp, hazard_analysis, fmea, risk_controls_doc, residual_risk, rmf)
  - Design Controls (design_inputs_doc, design_outputs_doc)
  - Verification & Validation (vv_evidence)
  - Traceability (traceability_matrix)
  - “Other Documents” (up to 6 most-recent docs not in the above)
- Each row includes:
  - Name
  - Status (derived)
  - Updated timestamp
  - Optional tag: “Generated from project setup”

### Critical UX constraints

- Never imply approvals or completion automatically.
- “Generate initial drafts” must be **deterministic** and **non-overwriting** (only fills eligible starter/empty docs).
- Any AI-related actions must be clearly labeled as draft/example and never overwrite user-authored content.

## Navigation summary

- Global dashboard: `/` or `/dashboard`
- Project dashboard: `/projects/:projectId/dashboard`
- Projects list: `/projects`
- Project docs list: `/projects/:projectId/documents`
- Documentation hub: `/projects/:projectId/docs`
- Project setup wizard: `/projects/:projectId/setup`

