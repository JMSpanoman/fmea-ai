import React, { useEffect, useMemo, useState } from 'react';
import { documentsApi } from '../../services/apiPhase3';

type GuidanceEntry = {
  purpose_text: string;
  population_text: string;
  ai_available: boolean;
  ai_button_text?: string;
};

let cachedRegistry: Record<string, GuidanceEntry> | null = null;
let cachedRegistryPromise: Promise<Record<string, GuidanceEntry>> | null = null;

async function loadGuidanceRegistry(): Promise<Record<string, GuidanceEntry>> {
  if (cachedRegistry) return cachedRegistry;
  if (!cachedRegistryPromise) {
    cachedRegistryPromise = documentsApi.getGuidanceRegistry().then((r) => (r || {}) as Record<string, GuidanceEntry>);
  }
  cachedRegistry = await cachedRegistryPromise;
  return cachedRegistry;
}

export default function DocumentGuidanceHeader({
  documentType,
  hasAiSample,
  onGenerateAiSample,
  onGenerateWithAi,
  isGeneratingAi,
  populationSources,
}: {
  documentType: string;
  hasAiSample: boolean;
  onGenerateAiSample?: () => void;
  onGenerateWithAi?: () => void;
  isGeneratingAi?: boolean;
  populationSources?: string[];
}) {
  const [loading, setLoading] = useState(false);
  const [registry, setRegistry] = useState<Record<string, GuidanceEntry> | null>(cachedRegistry);

  useEffect(() => {
    let alive = true;
    if (!registry) {
      setLoading(true);
      loadGuidanceRegistry()
        .then((r) => {
          if (!alive) return;
          setRegistry(r);
        })
        .catch(() => {
          if (!alive) return;
          setRegistry({});
        })
        .finally(() => {
          if (!alive) return;
          setLoading(false);
        });
    }
    return () => {
      alive = false;
    };
  }, [registry]);

  const guidance = useMemo(() => {
    const key = (documentType || '').toLowerCase();
    return key && registry ? registry[key] : null;
  }, [documentType, registry]);

  const showGenerateWithAi = typeof onGenerateWithAi === 'function';
  const generating = Boolean(isGeneratingAi);
  const dt = (documentType || '').toLowerCase();
  // RMF: "Generate with AI" runs deterministic compile (no LLM); hide AI sample (would corrupt compiled HTML).
  const showAiSampleButton = typeof onGenerateAiSample === 'function' && dt !== 'rmf';
  const generateWithAiLabel = dt === 'rmf' ? 'Refresh compiled RMF index' : 'Generate with AI';

  return (
    <div className="mb-4 rounded-xl border border-gray-200 bg-white p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <div className="text-sm font-semibold text-gray-900">What this document is for</div>
            <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700">
              {documentType}
            </span>
            {hasAiSample ? (
              <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                AI sample present
              </span>
            ) : null}
          </div>

          <div className="mt-1 text-sm text-gray-700">
            {loading ? 'Loading guidance…' : guidance?.purpose_text || '—'}
          </div>

          <div className="mt-3 text-sm font-semibold text-gray-900">How SmartQS populates it</div>
          <div className="mt-1 text-sm text-gray-700">
            {loading ? 'Loading guidance…' : guidance?.population_text || '—'}
          </div>

          {populationSources && populationSources.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {populationSources.map((s) => (
                <span
                  key={s}
                  className="rounded-full border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-700"
                >
                  {s}
                </span>
              ))}
            </div>
          ) : null}
        </div>

        {showGenerateWithAi ? (
          <div className="shrink-0">
            <div className="flex flex-col gap-2">
              <button
                onClick={onGenerateWithAi}
                disabled={generating}
                className="inline-flex items-center justify-center rounded-md bg-primary px-3 py-2 text-sm font-medium text-gray-900 hover:bg-primary/90 disabled:opacity-60"
              >
                {generating ? 'Working…' : generateWithAiLabel}
              </button>
              {showAiSampleButton && !hasAiSample ? (
                <button
                  onClick={onGenerateAiSample}
                  disabled={generating}
                  className="inline-flex items-center justify-center rounded-md border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-900 hover:bg-gray-50 disabled:opacity-60"
                >
                  Generate AI sample
                </button>
              ) : null}
            </div>
            <div className="mt-2 max-w-[280px] text-xs text-gray-500">
              AI output is an example draft only and must be reviewed before use.
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

