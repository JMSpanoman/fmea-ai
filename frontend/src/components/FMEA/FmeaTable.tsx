import React, { Fragment, useState } from 'react';
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
  Collapse,
  Button,
} from '@mui/material';
import { Edit, History, AutoAwesome, Science, ExpandMore, ExpandLess } from '@mui/icons-material';
import { FmeaRow } from '../../types';
import { RiskClassificationBadge, ReviewFlagBadge } from '../riskRuleEngine/RiskClassificationBadge';
import { RuleEngineExplanationPanel } from '../riskRuleEngine/RuleEngineExplanationPanel';

const DETAIL_COL_SPAN = 20;

interface FmeaTableProps {
  fmeaRows: FmeaRow[];
  projectId?: string;
  componentNameById?: Record<string, string>;
  onEdit?: (row: FmeaRow) => void;
  onViewHistory?: (row: FmeaRow) => void;
  onAiSuggest?: (row: FmeaRow) => void;
  onGenerateVV?: (row: FmeaRow) => void;
  onReevaluateRow?: (row: FmeaRow) => Promise<void>;
  reevaluateRowId?: string | null;
}

const FmeaTable: React.FC<FmeaTableProps> = ({
  fmeaRows,
  projectId,
  componentNameById,
  onEdit,
  onViewHistory,
  onAiSuggest,
  onGenerateVV,
  onReevaluateRow,
  reevaluateRowId,
}) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);
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

  const toggleExpand = (id: string) => {
    setExpandedId((cur) => (cur === id ? null : id));
  };

  return (
    <TableContainer component={Paper} sx={{ mt: 4, boxShadow: 3 }}>
      <Typography variant="h6" sx={{ p: 2 }}>
        FMEA Table
      </Typography>
      <Table sx={{ minWidth: 1600 }} aria-label="FMEA Table">
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
            <TableCell>Initial accept.</TableCell>
            <TableCell>Residual accept.</TableCell>
            <TableCell>Review flags</TableCell>
            <TableCell>Financial Impact</TableCell>
            <TableCell>Version</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {fmeaRows.map((row, idx) => (
            <Fragment key={row.id}>
              <TableRow hover>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', alignItems: 'center' }}>
                    <Tooltip title={expandedId === row.id ? 'Hide explanation' : 'Why? — rule engine'}>
                      <IconButton size="small" onClick={() => toggleExpand(row.id)}>
                        {expandedId === row.id ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
                      </IconButton>
                    </Tooltip>
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
                <TableCell>{row.severity ?? '-'}</TableCell>
                <TableCell>{row.probability ?? '-'}</TableCell>
                <TableCell>{row.detection ?? '-'}</TableCell>
                <TableCell>
                  <Chip label={row.rpn ?? '-'} size="small" color={getRpnColor(row.rpn)} />
                </TableCell>
                <TableCell>{row.mitigation || '-'}</TableCell>
                <TableCell>{row.residual_severity ?? '-'}</TableCell>
                <TableCell>{row.residual_probability ?? '-'}</TableCell>
                <TableCell>{row.residual_detection ?? '-'}</TableCell>
                <TableCell>
                  <Chip label={row.residual_rpn ?? '-'} size="small" color={getRpnColor(row.residual_rpn)} />
                </TableCell>
                <TableCell>
                  <RiskClassificationBadge classification={row.initial_risk_classification} />
                </TableCell>
                <TableCell>
                  <RiskClassificationBadge classification={row.residual_risk_classification} />
                </TableCell>
                <TableCell sx={{ maxWidth: 200 }}>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    <ReviewFlagBadge label="Benefit–risk" active={!!row.benefit_risk_required} />
                    <ReviewFlagBadge label="Critical fn" active={!!row.critical_function_flag} />
                    {row.approval_blocked ? (
                      <Chip size="small" label="Blocked" color="warning" variant="outlined" />
                    ) : null}
                  </Box>
                </TableCell>
                <TableCell>
                  {row.financial_impact ? `$${row.financial_impact.toLocaleString()}` : '-'}
                </TableCell>
                <TableCell>
                  <Chip label={`v${row.version}`} size="small" variant="outlined" />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ py: 0, borderBottom: expandedId === row.id ? undefined : 0 }} colSpan={DETAIL_COL_SPAN}>
                  <Collapse in={expandedId === row.id} timeout="auto" unmountOnExit>
                    <Box sx={{ py: 2 }}>
                      <RuleEngineExplanationPanel ruleEngineResult={row.rule_engine_result_json} />
                      {onReevaluateRow && projectId ? (
                        <Box sx={{ mt: 2 }}>
                          <Button
                            size="small"
                            variant="outlined"
                            disabled={reevaluateRowId === row.id}
                            onClick={async () => {
                              await onReevaluateRow(row);
                            }}
                          >
                            {reevaluateRowId === row.id ? 'Re-evaluating…' : 'Re-run rule engine (initial + residual)'}
                          </Button>
                        </Box>
                      ) : null}
                    </Box>
                  </Collapse>
                </TableCell>
              </TableRow>
            </Fragment>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default FmeaTable;
