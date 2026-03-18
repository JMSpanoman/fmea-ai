import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  IconButton,
  Chip,
  Tooltip,
  Box,
} from '@mui/material';
import { Edit, History, AutoAwesome, Science } from '@mui/icons-material';
import { FmeaRow } from '../../types';

interface FmeaTableProps {
  fmeaRows: FmeaRow[];
  projectId?: string;
  componentNameById?: Record<string, string>;
  onEdit?: (row: FmeaRow) => void;
  onViewHistory?: (row: FmeaRow) => void;
  onAiSuggest?: (row: FmeaRow) => void;
  onGenerateVV?: (row: FmeaRow) => void;
}

const FmeaTable: React.FC<FmeaTableProps> = ({
  fmeaRows,
  projectId,
  componentNameById,
  onEdit,
  onViewHistory,
  onAiSuggest,
  onGenerateVV,
}) => {
  const formatDisplayId = (idx: number) => `FMEA-${String(idx + 1).padStart(2, '0')}`;

  const getRpnColor = (rpn?: number): 'default' | 'error' | 'warning' | 'success' => {
    if (!rpn) return 'default';
    if (rpn >= 200) return 'error';
    if (rpn >= 100) return 'warning';
    return 'success';
  };

  const getComponentLabel = (row: FmeaRow) => {
    const id = row.component_id || '';
    if (id && componentNameById && componentNameById[id]) return componentNameById[id];
    const metaName = row.ai_metadata && (row.ai_metadata as any).component_name;
    if (typeof metaName === 'string' && metaName.trim()) return metaName.trim();
    return id || '-';
  };

  return (
    <TableContainer component={Paper} sx={{ mt: 4, boxShadow: 3 }}>
      <Typography variant="h6" sx={{ p: 2 }}>
        FMEA Table
      </Typography>
      <Table sx={{ minWidth: 1400 }} aria-label="FMEA Table">
        <TableHead>
          <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
            <TableCell>Actions</TableCell>
            <TableCell>ID</TableCell>
            <TableCell>Component</TableCell>
            <TableCell>Failure Mode</TableCell>
            <TableCell>Effect</TableCell>
            <TableCell>Cause</TableCell>
            <TableCell>Severity</TableCell>
            <TableCell>Probability</TableCell>
            <TableCell>Detection</TableCell>
            <TableCell>RPN</TableCell>
            <TableCell>Mitigation</TableCell>
            <TableCell>Residual Severity</TableCell>
            <TableCell>Residual Probability</TableCell>
            <TableCell>Residual Detection</TableCell>
            <TableCell>Residual RPN</TableCell>
            <TableCell>Financial Impact</TableCell>
            <TableCell>Version</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {fmeaRows.map((row, idx) => (
            <TableRow key={row.id} hover>
              <TableCell>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  {onEdit && (
                    <Tooltip title="Edit">
                      <IconButton size="small" onClick={() => onEdit(row)}>
                        <Edit fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                  {onViewHistory && (
                    <Tooltip title="Version History">
                      <IconButton size="small" onClick={() => onViewHistory(row)}>
                        <History fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                  {onAiSuggest && (
                    <Tooltip title="AI Suggestions">
                      <IconButton size="small" onClick={() => onAiSuggest(row)}>
                        <AutoAwesome fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                  {onGenerateVV && (
                    <Tooltip title="Generate V&V">
                      <IconButton size="small" onClick={() => onGenerateVV(row)}>
                        <Science fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </TableCell>
              <TableCell>{formatDisplayId(idx)}</TableCell>
              <TableCell>
                {projectId && row.component_id ? (
                  <Link
                    to={`/projects/${projectId}/components/${row.component_id}`}
                    className="text-primary hover:underline"
                  >
                    {getComponentLabel(row)}
                  </Link>
                ) : (
                  getComponentLabel(row)
                )}
              </TableCell>
              <TableCell>{row.failure_mode || '-'}</TableCell>
              <TableCell>{row.effect || '-'}</TableCell>
              <TableCell>{row.cause || '-'}</TableCell>
              <TableCell>{row.severity || '-'}</TableCell>
              <TableCell>{row.probability || '-'}</TableCell>
              <TableCell>{row.detection || '-'}</TableCell>
              <TableCell>
                <Chip
                  label={row.rpn || '-'}
                  size="small"
                  color={getRpnColor(row.rpn)}
                />
              </TableCell>
              <TableCell>{row.mitigation || '-'}</TableCell>
              <TableCell>{row.residual_severity || '-'}</TableCell>
              <TableCell>{row.residual_probability || '-'}</TableCell>
              <TableCell>{row.residual_detection || '-'}</TableCell>
              <TableCell>
                <Chip
                  label={row.residual_rpn || '-'}
                  size="small"
                  color={getRpnColor(row.residual_rpn)}
                />
              </TableCell>
              <TableCell>
                {row.financial_impact
                  ? `$${row.financial_impact.toLocaleString()}`
                  : '-'}
              </TableCell>
              <TableCell>
                <Chip label={`v${row.version}`} size="small" variant="outlined" />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default FmeaTable;
