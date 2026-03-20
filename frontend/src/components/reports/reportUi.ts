/**
 * Shared Tailwind class fragments for Smart FMEA / risk report UI.
 * Single source for typography, surfaces, and controls — keeps sections visually aligned.
 */
export const reportUi = {
  overline: 'text-[11px] font-semibold uppercase tracking-[0.12em] text-neutral-500',
  labelUpper: 'text-[10px] font-semibold uppercase tracking-wider text-neutral-500',
  titleSm: 'text-sm font-semibold tracking-tight text-neutral-900',
  titleBase: 'text-base font-semibold tracking-tight text-neutral-900',
  titleLg: 'text-lg font-semibold tracking-tight text-neutral-900',
  subtitle: 'text-sm leading-relaxed text-neutral-600',
  body: 'text-sm leading-relaxed text-neutral-700',
  bodyTight: 'text-sm text-neutral-700',
  caption: 'text-xs text-neutral-500',
  captionLead: 'text-xs leading-relaxed text-neutral-500',
  dt: 'text-xs font-semibold uppercase tracking-wider text-neutral-500',
  dd: 'mt-0.5 text-neutral-700',
  inlineCode:
    'rounded border border-neutral-200 bg-neutral-100 px-1 py-0.5 font-mono text-[11px] text-neutral-800',

  /** Primary card / panel on white chrome */
  card: 'rounded-lg border border-neutral-200 bg-white',
  cardPad: 'rounded-lg border border-neutral-200 bg-white p-4 sm:p-5',
  panelMuted: 'rounded-lg border border-neutral-200 bg-neutral-50/90',
  panelMutedPad: 'rounded-lg border border-neutral-200 bg-neutral-50/90 p-4',
  emptyDashed: 'rounded-lg border border-dashed border-neutral-300 bg-neutral-50/60',
  toolbar: 'rounded-lg border border-neutral-200 bg-white p-4',

  focusRing: 'focus:outline-none focus:ring-2 focus:ring-neutral-900/10 focus:border-neutral-400',
  select:
    'w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-900 disabled:cursor-not-allowed disabled:bg-neutral-100 disabled:text-neutral-400',
  /** Vertical rhythm between major report blocks */
  stackSection: 'space-y-5',
} as const;
