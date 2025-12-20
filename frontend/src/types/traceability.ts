/**
 * Canonical artifact types - matches backend enums
 * Used for type safety across traceability features
 */
export type ArtifactType =
  | "risk_item"
  | "risk_item_version"
  | "risk_control"
  | "design_input"
  | "design_output"
  | "vv_test"
  | "capa"
  | "change_control"
  | "fmea_row";

/**
 * Link type enum - matches backend LinkType
 */
export type LinkType =
  | "traces_to"
  | "verified_by"
  | "generated_from"
  | "impacts"
  | "mitigates"
  | "links_to";

