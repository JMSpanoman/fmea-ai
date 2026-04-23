/**
 * Post-market MAUDE → FMEA risk scoring API (Pro-gated).
 * Shapes mirror fmea_backend/schemas/postmarket_risk_scoring.py JSON.
 */
import api from '../axios';

export type RecentTrend = 'stable' | 'increasing' | 'decreasing' | 'insufficient_data';
export type ConfidenceLevel = 'low' | 'medium' | 'high';

export interface RelatedPhraseCount {
  phrase: string;
  count: number;
}

export interface OutcomeWeights {
  death: number;
  injury: number;
  malfunction: number;
  other: number;
  unknown: number;
}

export interface ProbabilityBandThresholds {
  min_weighted_for_2: number;
  min_weighted_for_3: number;
  min_weighted_for_4: number;
  min_weighted_for_5: number;
}

export interface TrendDetectionConfig {
  increasing_ratio: number;
  decreasing_ratio: number;
  min_events_per_half: number;
}

export interface PostmarketRiskScoringConfig {
  outcome_weights: OutcomeWeights;
  probability_thresholds: ProbabilityBandThresholds;
  trend: TrendDetectionConfig;
  max_failure_modes_returned: number;
  default_lookback_years: number;
}

export interface FailureModeScoreRequest {
  device_type: string;
  failure_mode: string;
  component?: string | null;
  date_from?: string | null;
  date_to?: string | null;
}

export interface FailureModeScoreResponse {
  suggested_probability_score: number;
  supporting_event_count: number;
  weighted_event_count: number;
  recent_trend: RecentTrend;
  confidence_level: ConfidenceLevel;
  rationale: string;
  top_related_effects: RelatedPhraseCount[];
  top_related_causes: RelatedPhraseCount[];
  device_type: string;
  component_filter?: string | null;
  failure_mode_query: string;
  date_from?: string | null;
  date_to?: string | null;
}

export interface ProjectRiskScoreItem {
  normalized_failure_mode: string;
  suggested_probability_score: number;
  supporting_event_count: number;
  weighted_event_count: number;
  recent_trend: RecentTrend;
  confidence_level: ConfidenceLevel;
  rationale: string;
  top_related_effects: RelatedPhraseCount[];
  top_related_causes: RelatedPhraseCount[];
  top_components: RelatedPhraseCount[];
}

export interface SuggestedMissingRisk {
  failure_mode_hint: string;
  weighted_event_count: number;
  supporting_event_count: number;
  rationale: string;
}

export interface DeviceFamilyAggregate {
  device_family: string;
  supporting_event_count: number;
  weighted_event_count: number;
}

export interface ComponentAggregate {
  component_text: string;
  supporting_event_count: number;
  weighted_event_count: number;
}

export interface ProjectRiskScoreResponse {
  project_id: string;
  device_type_used: string;
  date_from?: string | null;
  date_to?: string | null;
  config_snapshot: PostmarketRiskScoringConfig;
  device_family_aggregates: DeviceFamilyAggregate[];
  component_aggregates: ComponentAggregate[];
  items: ProjectRiskScoreItem[];
  suggested_missing_risks: SuggestedMissingRisk[];
}

export interface GetProjectRiskScoreOptions {
  /** Query param forwarded to GET /postmarket/risk-score/{id} */
  deviceType?: string;
}

export async function getProjectRiskScore(
  projectId: string,
  opts?: GetProjectRiskScoreOptions
): Promise<ProjectRiskScoreResponse> {
  const { data } = await api.get<ProjectRiskScoreResponse>(`/postmarket/risk-score/${projectId}`, {
    params: { device_type: opts?.deviceType || undefined },
  });
  return data;
}

// --- Pipeline + FMEA bridge (orchestrated post-market workflow) ---

export interface PostmarketIngestRequest {
  device_name: string;
  manufacturer_name?: string | null;
  generic_device_type?: string | null;
  date_from?: string | null;
  date_to?: string | null;
  max_records?: number;
  page_size?: number;
}

export interface PostmarketIngestResponse {
  fetched: number;
  inserted: number;
  skipped_duplicates: number;
  skipped_malformed: number;
  openfda_total_hint?: number | null;
  warnings: string[];
  /** Final openFDA search string after strategy / fallback selection. */
  search_query_used?: string;
  /** Label + query for each probe attempt (strict → broad). */
  query_attempts?: string[];
  /** Device tokens OR’d in generic/brand/openfda.device_name (includes synonyms). */
  expanded_device_terms?: string[];
  /** Sample FDA report ids from the first result page. */
  sample_source_report_keys?: string[];
}

export interface PostmarketExtractRequest {
  event_id?: string | null;
  event_ids?: string[] | null;
}

export interface PostmarketExtractResponse {
  requested: number;
  succeeded: number;
  failed: number;
  skipped: number;
  results: { event_id: string; status: string; extraction_id?: string | null; detail?: string | null }[];
}

export interface PostmarketRunPipelineRequest {
  project_id: string;
  device_type: string;
  device_name?: string | null;
  manufacturer_name?: string | null;
  generic_device_type?: string | null;
  component?: string | null;
  failure_mode?: string | null;
  date_from?: string | null;
  date_to?: string | null;
  run_ingestion?: boolean;
  run_extraction?: boolean;
  run_scoring?: boolean;
  max_ingest_records?: number;
  max_extract_events?: number;
}

export interface PostmarketScoringSummaryOut {
  device_type_used: string;
  date_from?: string | null;
  date_to?: string | null;
  failure_mode_themes_scored: number;
  suggested_missing_count: number;
}

export interface PostmarketRunPipelineResponse {
  records_fetched: number;
  records_inserted: number;
  records_skipped: number;
  records_extracted: number;
  extracted_failure_modes_count: number;
  scoring_summary?: PostmarketScoringSummaryOut | null;
  top_missing_risks: SuggestedMissingRisk[];
  status: 'completed' | 'partial' | 'failed';
  warnings: string[];
  disclaimer: string;
  pipeline_run_id?: string | null;
}

export interface PostmarketMatchedThemeOut {
  normalized_failure_mode: string;
  suggested_probability_score: number;
  supporting_event_count: number;
  weighted_event_count: number;
  matched_fmea_row_id?: string | null;
  matched_fmea_failure_mode?: string | null;
}

export interface PostmarketUnmatchedThemeOut {
  normalized_failure_mode: string;
  suggested_probability_score: number;
  supporting_event_count: number;
  weighted_event_count: number;
}

export interface PostmarketMissingRisksResponse {
  project_id: string;
  device_type_used: string;
  date_from?: string | null;
  date_to?: string | null;
  matched_themes: PostmarketMatchedThemeOut[];
  unmatched_themes: PostmarketUnmatchedThemeOut[];
  likely_missing_risks: SuggestedMissingRisk[];
  disclaimer: string;
}

export interface PostmarketAddMissingRiskToFmeaRequest {
  project_id: string;
  normalized_failure_mode: string;
  device_type?: string | null;
  component?: string | null;
  suggested_effect?: string | null;
  suggested_cause?: string | null;
  source_event_ids?: string[] | null;
}

export interface PostmarketAddMissingRiskToFmeaResponse {
  fmea_row_id: string;
  message: string;
  disclaimer: string;
}

export async function postmarketIngest(body: PostmarketIngestRequest): Promise<PostmarketIngestResponse> {
  const { data } = await api.post<PostmarketIngestResponse>('/postmarket/ingest', body);
  return data;
}

export async function postmarketExtract(body: PostmarketExtractRequest): Promise<PostmarketExtractResponse> {
  const { data } = await api.post<PostmarketExtractResponse>('/postmarket/extract', body);
  return data;
}

export async function runPostmarketPipeline(
  body: PostmarketRunPipelineRequest
): Promise<PostmarketRunPipelineResponse> {
  const { data } = await api.post<PostmarketRunPipelineResponse>('/postmarket/run-pipeline', body);
  return data;
}

export async function getPostmarketMissingRisks(
  projectId: string,
  opts?: { deviceType?: string }
): Promise<PostmarketMissingRisksResponse> {
  const { data } = await api.get<PostmarketMissingRisksResponse>(`/postmarket/missing-risks/${projectId}`, {
    params: { device_type: opts?.deviceType || undefined },
  });
  return data;
}

export async function addMissingPostmarketRiskToFmea(
  body: PostmarketAddMissingRiskToFmeaRequest
): Promise<PostmarketAddMissingRiskToFmeaResponse> {
  const { data } = await api.post<PostmarketAddMissingRiskToFmeaResponse>(
    '/postmarket/add-missing-risk-to-fmea',
    body
  );
  return data;
}

// --- Structured post-market report (POST /postmarket/report) ---

export interface PostmarketReportRequestPayload {
  project_id: string;
  device_type?: string | null;
  device_name?: string | null;
  component?: string | null;
  failure_mode?: string | null;
  date_from?: string | null;
  date_to?: string | null;
  include_missing_risks?: boolean;
  include_trend_summary?: boolean;
  include_outcome_breakdown?: boolean;
  max_failure_modes?: number;
  max_phrase_rows?: number;
}

export interface PostmarketReportPhraseRow {
  phrase: string;
  count: number;
  percentage_of_analyzed?: number | null;
}

export interface PostmarketReportOutcomeRow {
  outcome: 'malfunction' | 'injury' | 'death' | 'other' | 'unknown';
  count: number;
  percentage: number;
}

export interface PostmarketReportTrendPeriod {
  period_label: string;
  event_count: number;
}

export interface PostmarketReportTopFailureMode {
  normalized_failure_mode: string;
  supporting_event_count: number;
  weighted_event_count: number;
  top_related_components: PostmarketReportPhraseRow[];
  top_related_effects: PostmarketReportPhraseRow[];
  top_related_causes: PostmarketReportPhraseRow[];
  suggested_probability_score?: number | null;
  evidence_language_note?: string;
}

export interface PostmarketReportMissingRisk {
  normalized_failure_mode: string;
  component?: string | null;
  supporting_event_count: number;
  rationale: string;
  add_to_fmea_available: boolean;
  requires_expert_review?: boolean;
}

export type PostmarketReportMode = 'populated' | 'draft';

export interface PostmarketReportingPeriodPayload {
  date_from?: string | null;
  date_to?: string | null;
  label: string;
  markets_regions_note?: string | null;
}

export interface PostmarketDataSummaryPayload {
  maude_nlp_linked_records_reviewed: number;
  pms_signal_records_in_scope: number;
  unique_normalized_failure_modes: number;
  malfunction_outcome_events: number;
  injury_outcome_events: number;
  death_outcome_events: number;
  other_outcome_events: number;
  unknown_outcome_events: number;
  date_range_analyzed_start?: string | null;
  date_range_analyzed_end?: string | null;
}

export interface PostmarketTopFindingsPayload {
  top_failure_modes: PostmarketReportPhraseRow[];
  top_causes: PostmarketReportPhraseRow[];
  top_effects: PostmarketReportPhraseRow[];
  top_components: PostmarketReportPhraseRow[];
  trend_qualitative?: string | null;
}

export interface PmsSignalIdentifiedPayload {
  signal_id: string;
  description: string;
  source: string;
  status: string;
  notes?: string | null;
}

export interface PostmarketReportFmeaDraft {
  normalized_failure_mode: string;
  supporting_event_count: number;
  weighted_event_count?: number | null;
  rationale: string;
  requires_expert_review: boolean;
  add_to_fmea_available: boolean;
}

export interface PostmarketReportResponsePayload {
  /** Present on current API; omitted on older backends. */
  report_mode?: PostmarketReportMode;
  report_title: string;
  generated_at: string;
  project_summary: {
    project_id: string;
    project_name: string;
    project_description?: string | null;
  };
  filter_summary: {
    device_type_used: string;
    device_name_label?: string | null;
    component_filter?: string | null;
    failure_mode_filter?: string | null;
    date_from?: string | null;
    date_to?: string | null;
  };
  reporting_period?: PostmarketReportingPeriodPayload;
  summary?: PostmarketDataSummaryPayload;
  top_findings?: PostmarketTopFindingsPayload;
  signals_identified?: PmsSignalIdentifiedPayload[];
  recommended_actions?: string[];
  evidence_summary: {
    total_maude_records_analyzed: number;
    date_range_analyzed_start?: string | null;
    date_range_analyzed_end?: string | null;
    qualitative_summary: string;
    component_focus_note?: string | null;
  };
  top_failure_modes: PostmarketReportTopFailureMode[];
  top_causes: PostmarketReportPhraseRow[];
  top_effects: PostmarketReportPhraseRow[];
  outcome_breakdown: PostmarketReportOutcomeRow[];
  trend_summary?: {
    granularity: 'monthly' | 'quarterly';
    periods: PostmarketReportTrendPeriod[];
    qualitative_summary: string;
  } | null;
  missing_real_world_risks: PostmarketReportMissingRisk[];
  recommended_fmea_drafts: PostmarketReportFmeaDraft[];
  disclaimer: string;
  future_data_sources_placeholder: string;
}

export async function postPostmarketReport(
  body: PostmarketReportRequestPayload
): Promise<PostmarketReportResponsePayload> {
  const { data } = await api.post<PostmarketReportResponsePayload>('/postmarket/report', body);
  return data;
}

export async function postFailureModeScore(
  body: FailureModeScoreRequest
): Promise<FailureModeScoreResponse> {
  const { data } = await api.post<FailureModeScoreResponse>('/postmarket/risk-score/failure-mode', body);
  return data;
}

/** Sample mock for Storybook, tests, or offline UI demos (not used at runtime). */
export const MOCK_PROJECT_RISK_SCORE_RESPONSE: ProjectRiskScoreResponse = {
  project_id: 'proj_demo',
  device_type_used: 'infusion pump',
  date_from: '2020-01-01',
  date_to: '2025-01-01',
  config_snapshot: {
    outcome_weights: {
      death: 5,
      injury: 3,
      malfunction: 1,
      other: 1.5,
      unknown: 1.2,
    },
    probability_thresholds: {
      min_weighted_for_2: 3,
      min_weighted_for_3: 10,
      min_weighted_for_4: 25,
      min_weighted_for_5: 60,
    },
    trend: {
      increasing_ratio: 1.25,
      decreasing_ratio: 0.75,
      min_events_per_half: 3,
    },
    max_failure_modes_returned: 40,
    default_lookback_years: 5,
  },
  device_family_aggregates: [
    { device_family: 'Pump, Infusion', supporting_event_count: 120, weighted_event_count: 210 },
  ],
  component_aggregates: [
    { component_text: 'battery', supporting_event_count: 34, weighted_event_count: 52 },
    { component_text: 'display', supporting_event_count: 18, weighted_event_count: 22 },
  ],
  items: [
    {
      normalized_failure_mode: 'power loss / unexpected shutdown',
      suggested_probability_score: 4,
      supporting_event_count: 28,
      weighted_event_count: 44,
      recent_trend: 'increasing',
      confidence_level: 'medium',
      rationale:
        'Weighted MAUDE-linked narratives in the lookback window exceed mid-band thresholds; trend split suggests late-window elevation.',
      top_related_effects: [
        { phrase: 'therapy interruption', count: 12 },
        { phrase: 'under-infusion', count: 7 },
      ],
      top_related_causes: [
        { phrase: 'battery depletion', count: 9 },
        { phrase: 'electrical fault', count: 5 },
      ],
      top_components: [{ phrase: 'battery', count: 11 }],
    },
  ],
  suggested_missing_risks: [
    {
      failure_mode_hint: 'air-in-line false alarm cluster',
      weighted_event_count: 18,
      supporting_event_count: 14,
      rationale:
        'Repeated post-market theme with limited overlap to normalized FMEA failure-mode phrases for this project.',
    },
  ],
};

export const MOCK_FAILURE_MODE_SCORE_RESPONSE: FailureModeScoreResponse = {
  suggested_probability_score: 3,
  supporting_event_count: 16,
  weighted_event_count: 24,
  recent_trend: 'stable',
  confidence_level: 'medium',
  rationale:
    'Event-weighted total maps to mid-range probability; corpus size supports moderate confidence with caveats on MAUDE reporting bias.',
  top_related_effects: [{ phrase: 'nuisance alarm', count: 6 }],
  top_related_causes: [{ phrase: 'sensor drift', count: 4 }],
  device_type: 'infusion pump',
  component_filter: 'sensor',
  failure_mode_query: 'false occlusion',
  date_from: '2022-01-01',
  date_to: '2025-01-01',
};
