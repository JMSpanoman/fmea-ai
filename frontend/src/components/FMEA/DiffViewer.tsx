import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
} from '@mui/material';
import { FmeaVersion } from '../../types';

interface DiffViewerProps {
  open: boolean;
  onClose: () => void;
  versions: FmeaVersion[];
  currentRow: any;
}

const DiffViewer: React.FC<DiffViewerProps> = ({ open, onClose, versions, currentRow }) => {
  const getFieldLabel = (key: string): string => {
    const labels: Record<string, string> = {
      failure_mode: 'Failure Mode',
      effect: 'Effect',
      cause: 'Cause',
      severity: 'Severity',
      probability: 'Probability',
      detection: 'Detection',
      rpn: 'RPN',
      mitigation: 'Mitigation',
      residual_severity: 'Residual Severity',
      residual_probability: 'Residual Probability',
      residual_detection: 'Residual Detection',
      residual_rpn: 'Residual RPN',
      financial_impact: 'Financial Impact',
      component_id: 'Component',
    };
    return labels[key] || key;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>Version History</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Current Version: {currentRow?.version || 1}
          </Typography>
        </Box>

        {versions.length === 0 ? (
          <Typography color="text.secondary">No version history available</Typography>
        ) : (
          versions.map((version, index) => (
            <Box key={version.id} sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Version {version.version} - {new Date(version.created_at).toLocaleString()}
              </Typography>

              {version.diff && Object.keys(version.diff).length > 0 ? (
                <TableContainer component={Paper} sx={{ mt: 1 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Field</TableCell>
                        <TableCell>Old Value</TableCell>
                        <TableCell>New Value</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(version.diff).map(([key, change]: [string, any]) => (
                        <TableRow key={key}>
                          <TableCell>
                            <strong>{getFieldLabel(key)}</strong>
                          </TableCell>
                          <TableCell>
                            {change.old !== null && change.old !== undefined ? (
                              <Chip
                                label={String(change.old)}
                                size="small"
                                color="error"
                                variant="outlined"
                              />
                            ) : (
                              <Typography variant="body2" color="text.secondary">
                                (empty)
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell>
                            {change.new !== null && change.new !== undefined ? (
                              <Chip
                                label={String(change.new)}
                                size="small"
                                color="success"
                                variant="outlined"
                              />
                            ) : (
                              <Typography variant="body2" color="text.secondary">
                                (empty)
                              </Typography>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  No changes recorded for this version
                </Typography>
              )}
            </Box>
          ))
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default DiffViewer;

