import React from 'react';
import { MenuItem, Select, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';

const OPTIONS = ['Acceptable', 'ALARP', 'Unacceptable'] as const;

export type MatrixState = Record<string, Record<string, string>>;

interface RiskCriteriaMatrixProps {
  matrix: MatrixState;
  severityLevels: number;
  probabilityLevels: number;
  onChange: (next: MatrixState) => void;
  readOnly?: boolean;
}

export function RiskCriteriaMatrix({
  matrix,
  severityLevels,
  probabilityLevels,
  onChange,
  readOnly,
}: RiskCriteriaMatrixProps) {
  const setCell = (si: number, pi: number, value: string) => {
    const rowKey = String(si);
    const colKey = String(pi);
    const next = { ...matrix, [rowKey]: { ...(matrix[rowKey] || {}), [colKey]: value } };
    onChange(next);
  };

  return (
    <div>
      <Typography variant="subtitle2" gutterBottom>
        Risk acceptability matrix (severity × probability)
      </Typography>
      <Table size="small" sx={{ maxWidth: 720, border: '1px solid #e5e7eb' }}>
        <TableHead>
          <TableRow sx={{ bgcolor: '#f9fafb' }}>
            <TableCell sx={{ fontWeight: 700 }}>S \\ P</TableCell>
            {Array.from({ length: probabilityLevels }, (_, i) => (
              <TableCell key={i} align="center" sx={{ fontWeight: 700 }}>
                P{i + 1}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {Array.from({ length: severityLevels }, (_, si) => (
            <TableRow key={si}>
              <TableCell sx={{ fontWeight: 600, bgcolor: '#fafafa' }}>S{si + 1}</TableCell>
              {Array.from({ length: probabilityLevels }, (_, pi) => {
                const v = matrix[String(si + 1)]?.[String(pi + 1)] || '';
                return (
                  <TableCell key={pi} align="center" sx={{ minWidth: 120 }}>
                    {readOnly ? (
                      v || '—'
                    ) : (
                      <Select
                        size="small"
                        fullWidth
                        value={v || ''}
                        displayEmpty
                        onChange={(e) => setCell(si + 1, pi + 1, String(e.target.value))}
                      >
                        <MenuItem value="">
                          <em>Select</em>
                        </MenuItem>
                        {OPTIONS.map((o) => (
                          <MenuItem key={o} value={o}>
                            {o}
                          </MenuItem>
                        ))}
                      </Select>
                    )}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
