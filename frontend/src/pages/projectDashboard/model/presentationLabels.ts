/**
 * Presentation-only label mapping.
 * Domain/API values are unchanged; "Unknown" is shown as "Not evaluated yet".
 */
export const NOT_EVALUATED_YET = 'Not evaluated yet';

export function toPresentationUnknown(value: string | null | undefined): string {
  if (value == null || value === '') return NOT_EVALUATED_YET;
  if (value.trim().toLowerCase() === 'unknown') return NOT_EVALUATED_YET;
  return value;
}
