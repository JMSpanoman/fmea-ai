import React from 'react';
import { Chip, ChipProps } from '@mui/material';

/** UI-only mapping: classification strings → MUI Chip presentation (not used in backend logic). */
const CLASSIFICATION_STYLE: Record<
  string,
  { label: string; color: ChipProps['color']; variant?: ChipProps['variant'] }
> = {
  Acceptable: { label: 'Acceptable', color: 'success', variant: 'filled' },
  ALARP: { label: 'ALARP', color: 'warning', variant: 'filled' },
  Unacceptable: { label: 'Unacceptable', color: 'error', variant: 'filled' },
};

export function RiskClassificationBadge({ classification }: { classification?: string | null }) {
  const c = (classification || '').trim();
  if (!c) {
    return <Chip size="small" label="—" variant="outlined" />;
  }
  const style = CLASSIFICATION_STYLE[c] || { label: c, color: 'default' as const, variant: 'outlined' as const };
  return <Chip size="small" label={style.label} color={style.color} variant={style.variant || 'outlined'} />;
}

export function ReviewFlagBadge({ label, active }: { label: string; active: boolean }) {
  if (!active) return null;
  return <Chip size="small" label={label} color="info" variant="outlined" sx={{ mr: 0.5, mb: 0.5 }} />;
}
