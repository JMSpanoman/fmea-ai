import React from 'react';
import type { RiskRowFilter, SavedReportView } from './reportFmeaCompliance';
import { SAVED_VIEW_PRESETS } from './reportFmeaCompliance';
import { reportUi } from './reportUi';

type ReportViewToolbarProps = {
  fmeaActive: boolean;
  savedView: SavedReportView;
  onSavedView: (v: SavedReportView) => void;
  riskFilter: RiskRowFilter;
  onRiskFilter: (f: RiskRowFilter) => void;
  complianceMode: boolean;
  onComplianceMode: (on: boolean) => void;
};

const FILTER_OPTIONS: { value: RiskRowFilter; label: string }[] = [
  { value: 'all', label: 'All rows' },
  { value: 'high', label: 'High risk (RPN ≥ 100)' },
  { value: 'medium', label: 'Medium risk (50–99)' },
  { value: 'low', label: 'Low risk (1–49)' },
  { value: 'unmitigated', label: 'Unmitigated only' },
  { value: 'needs_review', label: 'Needs review' },
  { value: 'closed', label: 'Closed / complete (low + mitigated)' },
];

export function ReportViewToolbar({
  fmeaActive,
  savedView,
  onSavedView,
  riskFilter,
  onRiskFilter,
  complianceMode,
  onComplianceMode,
}: ReportViewToolbarProps) {
  return (
    <div className={reportUi.toolbar}>
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 space-y-2">
          <p className={reportUi.overline}>Saved view</p>
          <div className="flex flex-wrap gap-2">
            {(Object.keys(SAVED_VIEW_PRESETS) as SavedReportView[]).map((key) => {
              const p = SAVED_VIEW_PRESETS[key];
              const active = savedView === key;
              return (
                <button
                  key={key}
                  type="button"
                  title={p.description}
                  onClick={() => onSavedView(key)}
                  className={`rounded-md border px-3 py-2 text-sm font-medium transition ${
                    active
                      ? 'border-neutral-900 bg-neutral-900 text-white'
                      : 'border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50'
                  }`}
                >
                  {p.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex w-full min-w-0 flex-col gap-3 sm:max-w-md sm:flex-row sm:items-end sm:gap-4 lg:w-auto lg:max-w-none">
          <div className="min-w-0 flex-1 sm:min-w-[12rem]">
            <label htmlFor="report-row-filter" className={`mb-1 block ${reportUi.overline}`}>
              Row filter
            </label>
            <select
              id="report-row-filter"
              value={riskFilter}
              disabled={!fmeaActive}
              onChange={(e) => onRiskFilter(e.target.value as RiskRowFilter)}
              className={`${reportUi.select} ${reportUi.focusRing}`}
            >
              {FILTER_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
            {!fmeaActive ? <p className={`mt-1 ${reportUi.caption}`}>Row filters apply to FMEA table preview only.</p> : null}
          </div>

          <label className="flex cursor-pointer items-center gap-2 rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-neutral-300 text-neutral-900 focus:ring-neutral-900/20"
              checked={complianceMode}
              disabled={!fmeaActive}
              onChange={(e) => onComplianceMode(e.target.checked)}
            />
            <span className="text-sm font-medium text-neutral-800">Compliance mode</span>
          </label>
          {!fmeaActive ? <span className={`${reportUi.caption} sm:pb-2`}>FMEA only</span> : null}
        </div>
      </div>
    </div>
  );
}
