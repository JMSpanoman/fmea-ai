/**
 * SmartRisk SaaS Feature Flags
 *
 * Centralized plan-based feature configuration.
 * Compatible with future Stripe subscription tiers.
 *
 * Plans: lite | pro
 * Future: starter, enterprise, etc.
 */
export const PLAN_LITE = "lite" as const;
export const PLAN_PRO = "pro" as const;

export type Plan = typeof PLAN_LITE | typeof PLAN_PRO;

export interface FeatureFlags {
  // Lite features
  aiFmea: boolean;
  editableFmeaTable: boolean;
  liveRpnCalculation: boolean;
  csvExport: boolean;

  // Pro-only features
  projects: boolean;
  versionControl: boolean;
  diffViewer: boolean;
  traceabilityMatrix: boolean;
  capaGenerator: boolean;
  designControls: boolean;
  mitigationLibrary: boolean;
  aiSuggestionHistoryLogging: boolean;
  scheduledReviewReminders: boolean;
  commentsCollaboration: boolean;

  // Derived
  documentControl: boolean;
  riskItems: boolean;
  hazardAnalysis: boolean;
  rmf: boolean;
  residualRisk: boolean;
  pms: boolean;
  vvTests: boolean;
  audits: boolean;
  training: boolean;
  changeControl: boolean;
  ncr: boolean;
  complaints: boolean;
  equipment: boolean;
  suppliers: boolean;
}

const FEATURES_LITE: FeatureFlags = {
  aiFmea: true,
  editableFmeaTable: true,
  liveRpnCalculation: true,
  csvExport: true,

  projects: false,
  versionControl: false,
  diffViewer: false,
  traceabilityMatrix: false,
  capaGenerator: false,
  designControls: false,
  mitigationLibrary: false,
  aiSuggestionHistoryLogging: false,
  scheduledReviewReminders: false,
  commentsCollaboration: false,

  documentControl: false,
  riskItems: false,
  hazardAnalysis: false,
  rmf: false,
  residualRisk: false,
  pms: false,
  vvTests: false,
  audits: false,
  training: false,
  changeControl: false,
  ncr: false,
  complaints: false,
  equipment: false,
  suppliers: false,
};

const FEATURES_PRO: FeatureFlags = {
  ...FEATURES_LITE,
  projects: true,
  versionControl: true,
  diffViewer: true,
  traceabilityMatrix: true,
  capaGenerator: true,
  designControls: true,
  mitigationLibrary: true,
  aiSuggestionHistoryLogging: true,
  scheduledReviewReminders: true,
  commentsCollaboration: true,

  documentControl: true,
  riskItems: true,
  hazardAnalysis: true,
  rmf: true,
  residualRisk: true,
  pms: true,
  vvTests: true,
  audits: true,
  training: true,
  changeControl: true,
  ncr: true,
  complaints: true,
  equipment: true,
  suppliers: true,
};

export const featuresByPlan: Record<Plan, FeatureFlags> = {
  [PLAN_LITE]: FEATURES_LITE,
  [PLAN_PRO]: FEATURES_PRO,
};

/**
 * Get feature flags for a given plan.
 * Defaults to lite if plan is unknown.
 */
export function getFeatures(plan: string | null | undefined): FeatureFlags {
  const p = (plan || PLAN_LITE).toLowerCase();
  return featuresByPlan[p as Plan] ?? FEATURES_LITE;
}

/**
 * Check if user has Pro plan.
 */
export function isProPlan(plan: string | null | undefined): boolean {
  return (plan || PLAN_LITE).toLowerCase() === PLAN_PRO;
}

/**
 * Use full SmartRisk Pro in the browser when developing locally.
 * - `npm run dev`: import.meta.env.DEV is true
 * - `npm run preview` on localhost: env vars from .env.local are NOT re-read unless you rebuild;
 *   this hostname check still upgrades the UI to Pro without a rebuild.
 *
 * Opt out on localhost: set `VITE_FORCE_PLAN=lite` in .env.local and rebuild (or use dev server).
 */
export function defaultToProPlanForLocalUi(): boolean {
  if (import.meta.env.DEV) return true;
  if (typeof window === 'undefined') return false;
  const h = window.location.hostname;
  return h === 'localhost' || h === '127.0.0.1' || h === '[::1]';
}

/** Nav item with optional plan requirement */
export interface NavItemConfig {
  path: string;
  label: string;
  icon: string;
  section: string;
  kind: string;
  groupId?: string;
  /** If set, only show for this plan or higher */
  requiresPro?: boolean;
}
