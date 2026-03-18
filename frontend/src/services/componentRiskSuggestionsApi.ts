/**
 * API for component-scoped risk suggestions (generate, list, reject, accept).
 */
import api from '../axios';

export interface SuggestedFailureModeOut {
  id: string;
  suggestion_set_id: string;
  text: string;
  created_at?: string | null;
}

export interface SuggestedHazardOut {
  id: string;
  suggestion_set_id: string;
  text: string;
  hazard_library_id?: string | null;
  created_at?: string | null;
}

export interface SuggestedHazardousSituationOut {
  id: string;
  suggestion_set_id: string;
  text: string;
  created_at?: string | null;
}

export interface SuggestedHarmOut {
  id: string;
  suggestion_set_id: string;
  text: string;
  harm_library_id?: string | null;
  created_at?: string | null;
}

export interface SuggestedControlOut {
  id: string;
  suggestion_set_id: string;
  text: string;
  risk_control_library_id?: string | null;
  created_at?: string | null;
}

export interface SuggestedVerificationMethodOut {
  id: string;
  suggestion_set_id: string;
  text: string;
  verification_library_id?: string | null;
  created_at?: string | null;
}

export interface SuggestionSetOut {
  id: string;
  source_type: string;
  source_id: string;
  architecture_id?: string | null;
  project_id?: string | null;
  rule_id: string;
  created_at?: string | null;
  failure_modes: SuggestedFailureModeOut[];
  hazards: SuggestedHazardOut[];
  hazardous_situations: SuggestedHazardousSituationOut[];
  harms: SuggestedHarmOut[];
  controls: SuggestedControlOut[];
  verification_methods: SuggestedVerificationMethodOut[];
}

export interface GenerateSuggestionsResponse {
  created: number;
}

export interface ControlAcceptItem {
  control_text?: string | null;
  risk_control_library_id?: string | null;
}

export interface VerificationAcceptItem {
  verification_text?: string | null;
  verification_library_id?: string | null;
}

export interface AcceptSuggestionRequest {
  failure_mode?: string | null;
  hazard?: string | null;
  hazardous_situation?: string | null;
  harm?: string | null;
  control?: string | null;
  verification?: string | null;
  hazard_library_id?: string | null;
  harm_library_id?: string | null;
  controls?: ControlAcceptItem[] | null;
  verifications?: VerificationAcceptItem[] | null;
}

export interface AcceptSuggestionResponse {
  risk_item_id: string;
  project_risk_item_id?: string | null;
}

function base(projectId: string, componentId: string) {
  return `/projects/${projectId}/components/${componentId}`;
}

export const componentRiskSuggestionsApi = {
  generate(
    projectId: string,
    componentId: string,
    options?: { regenerate?: boolean; only_active_rules?: boolean }
  ): Promise<GenerateSuggestionsResponse> {
    return api
      .post(`${base(projectId, componentId)}/generate-risk-suggestions`, options ?? {})
      .then((r) => r.data);
  },

  list(projectId: string, componentId: string): Promise<SuggestionSetOut[]> {
    return api.get(`${base(projectId, componentId)}/risk-suggestions`).then((r) => r.data);
  },

  deleteAll(projectId: string, componentId: string): Promise<void> {
    return api.delete(`${base(projectId, componentId)}/risk-suggestions`);
  },

  reject(
    projectId: string,
    componentId: string,
    suggestionSetId: string
  ): Promise<void> {
    return api.delete(
      `${base(projectId, componentId)}/risk-suggestions/${suggestionSetId}`
    );
  },

  accept(
    projectId: string,
    componentId: string,
    suggestionSetId: string,
    overrides?: AcceptSuggestionRequest
  ): Promise<AcceptSuggestionResponse> {
    return api
      .post(
        `${base(projectId, componentId)}/risk-suggestions/${suggestionSetId}/accept`,
        overrides ?? {}
      )
      .then((r) => r.data);
  },

  // ---------- Phase 3: Link suggestions to master libraries ----------
  updateHazardLibraryLink(
    projectId: string,
    componentId: string,
    suggestedHazardId: string,
    hazardLibraryId: string | null
  ): Promise<SuggestedHazardOut> {
    return api
      .patch(
        `${base(projectId, componentId)}/risk-suggestions/suggested-hazards/${suggestedHazardId}`,
        { hazard_library_id: hazardLibraryId }
      )
      .then((r) => r.data);
  },
  updateHarmLibraryLink(
    projectId: string,
    componentId: string,
    suggestedHarmId: string,
    harmLibraryId: string | null
  ): Promise<SuggestedHarmOut> {
    return api
      .patch(
        `${base(projectId, componentId)}/risk-suggestions/suggested-harms/${suggestedHarmId}`,
        { harm_library_id: harmLibraryId }
      )
      .then((r) => r.data);
  },
  updateControlLibraryLink(
    projectId: string,
    componentId: string,
    suggestedControlId: string,
    riskControlLibraryId: string | null
  ): Promise<SuggestedControlOut> {
    return api
      .patch(
        `${base(projectId, componentId)}/risk-suggestions/suggested-controls/${suggestedControlId}`,
        { risk_control_library_id: riskControlLibraryId }
      )
      .then((r) => r.data);
  },
  updateVerificationLibraryLink(
    projectId: string,
    componentId: string,
    suggestedVerificationId: string,
    verificationLibraryId: string | null
  ): Promise<SuggestedVerificationMethodOut> {
    return api
      .patch(
        `${base(projectId, componentId)}/risk-suggestions/suggested-verifications/${suggestedVerificationId}`,
        { verification_library_id: verificationLibraryId }
      )
      .then((r) => r.data);
  },

  createAndLinkHazard(
    projectId: string,
    componentId: string,
    suggestedHazardId: string
  ): Promise<SuggestedHazardOut> {
    return api
      .post(
        `${base(projectId, componentId)}/risk-suggestions/suggested-hazards/${suggestedHazardId}/create-and-link`
      )
      .then((r) => r.data);
  },
  createAndLinkHarm(
    projectId: string,
    componentId: string,
    suggestedHarmId: string
  ): Promise<SuggestedHarmOut> {
    return api
      .post(
        `${base(projectId, componentId)}/risk-suggestions/suggested-harms/${suggestedHarmId}/create-and-link`
      )
      .then((r) => r.data);
  },
  createAndLinkControl(
    projectId: string,
    componentId: string,
    suggestedControlId: string
  ): Promise<SuggestedControlOut> {
    return api
      .post(
        `${base(projectId, componentId)}/risk-suggestions/suggested-controls/${suggestedControlId}/create-and-link`
      )
      .then((r) => r.data);
  },
  createAndLinkVerification(
    projectId: string,
    componentId: string,
    suggestedVerificationId: string
  ): Promise<SuggestedVerificationMethodOut> {
    return api
      .post(
        `${base(projectId, componentId)}/risk-suggestions/suggested-verifications/${suggestedVerificationId}/create-and-link`
      )
      .then((r) => r.data);
  },
};
