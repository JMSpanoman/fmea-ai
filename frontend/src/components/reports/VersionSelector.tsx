import React from 'react';
import { reportUi } from './reportUi';

export type VersionOption = {
  value: number | 'current';
  label: string;
};

export type VersionSelectorProps = {
  label: string;
  value: number | 'current';
  options: VersionOption[];
  onChange: (v: number | 'current') => void;
  disabled?: boolean;
  id?: string;
};

export function VersionSelector({ label, value, options, onChange, disabled, id }: VersionSelectorProps) {
  return (
    <div className="flex min-w-0 flex-1 flex-col gap-1 sm:min-w-[200px] sm:flex-none">
      <label htmlFor={id} className={reportUi.overline}>
        {label}
      </label>
      <select
        id={id}
        disabled={disabled}
        className={`${reportUi.select} ${reportUi.focusRing}`}
        value={value === 'current' ? 'current' : String(value)}
        onChange={(e) => {
          const v = e.target.value;
          onChange(v === 'current' ? 'current' : Number(v));
        }}
      >
        {options.map((o) => (
          <option key={String(o.value)} value={o.value === 'current' ? 'current' : String(o.value)}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}
