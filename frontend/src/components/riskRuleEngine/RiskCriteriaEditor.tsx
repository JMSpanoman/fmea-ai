import React, { useEffect, useState } from 'react';
import type { ProjectRiskCriteria } from '../../services/riskRuleEngineApi';
import { RiskCriteriaMatrix, type MatrixState } from './RiskCriteriaMatrix';
import { Button, MenuItem, Select, TextField, Typography, FormControl, InputLabel, Alert } from '@mui/material';

const DEFAULT_LEVELS = 4;

function parseKeywords(text: string): string[] {
  return text
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean);
}

export function RiskCriteriaEditor({
  criteria,
  readOnly,
  onSave,
  validationErrors,
}: {
  criteria: ProjectRiskCriteria | null;
  readOnly?: boolean;
  onSave: (patch: Partial<ProjectRiskCriteria>) => Promise<void>;
  validationErrors?: string[];
}) {
  const [method, setMethod] = useState(criteria?.evaluation_method || 'matrix');
  const [matrix, setMatrix] = useState<MatrixState>(() => (criteria?.risk_matrix as MatrixState) || {});
  const [kwText, setKwText] = useState(() => {
    const list = (criteria?.special_rules as any)?.critical_function_keywords;
    return Array.isArray(list) ? list.join('\n') : '';
  });
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (criteria) {
      setMethod(criteria.evaluation_method || 'matrix');
      setMatrix((criteria.risk_matrix as MatrixState) || {});
      const list = (criteria.special_rules as any)?.critical_function_keywords;
      setKwText(Array.isArray(list) ? list.join('\n') : '');
    }
  }, [criteria?.id]);

  if (!criteria) {
    return <Typography color="text.secondary">No criteria version selected.</Typography>;
  }

  const handleSave = async () => {
    setErr(null);
    setSaving(true);
    try {
      const special = {
        ...((criteria.special_rules as object) || {}),
        critical_function_keywords: parseKeywords(kwText),
      };
      await onSave({
        evaluation_method: method,
        risk_matrix: matrix,
        special_rules: special,
      });
    } catch (e: any) {
      setErr(e?.message || 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      {validationErrors?.length ? (
        <Alert severity="warning">
          <div className="font-semibold mb-1">Matrix / criteria incomplete</div>
          <ul className="list-disc pl-5 text-sm">
            {validationErrors.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </Alert>
      ) : null}
      {err ? <Alert severity="error">{err}</Alert> : null}

      <FormControl size="small" sx={{ minWidth: 200 }} disabled={readOnly}>
        <InputLabel>Evaluation method</InputLabel>
        <Select label="Evaluation method" value={method} onChange={(e) => setMethod(String(e.target.value))}>
          <MenuItem value="matrix">Matrix (primary)</MenuItem>
          <MenuItem value="score">Numeric score thresholds</MenuItem>
          <MenuItem value="hybrid">Hybrid (conservative merge)</MenuItem>
        </Select>
      </FormControl>

      <RiskCriteriaMatrix
        matrix={matrix}
        severityLevels={DEFAULT_LEVELS}
        probabilityLevels={DEFAULT_LEVELS}
        onChange={setMatrix}
        readOnly={readOnly}
      />

      <div>
        <Typography variant="subtitle2" gutterBottom>
          Critical function keywords (one per line)
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
          Used for configurable text matching — keep device-specific hazards in data, not in code.
        </Typography>
        <TextField
          multiline
          minRows={4}
          fullWidth
          value={kwText}
          onChange={(e) => setKwText(e.target.value)}
          disabled={readOnly}
          placeholder="loss of pacing&#10;battery depletion"
        />
      </div>

      {!readOnly ? (
        <Button variant="contained" onClick={() => handleSave()} disabled={saving}>
          {saving ? 'Saving…' : 'Save draft'}
        </Button>
      ) : null}
    </div>
  );
}
