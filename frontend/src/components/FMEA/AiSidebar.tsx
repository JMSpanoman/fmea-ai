import React, { useState } from 'react';
import { Drawer, Box, Typography, Button, TextField, CircularProgress, Alert, Chip } from '@mui/material';
import { FmeaRow, AIFMEASuggestResponse } from '../../types';
import { aiApi } from '../../services/apiPhase1';

interface AiSidebarProps {
  open: boolean;
  onClose: () => void;
  fmeaRow: FmeaRow | null;
  onApply: (suggestions: AIFMEASuggestResponse) => void;
}

const AiSidebar: React.FC<AiSidebarProps> = ({ open, onClose, fmeaRow, onApply }) => {
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<AIFMEASuggestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [component, setComponent] = useState('');
  const [failureMode, setFailureMode] = useState('');
  const [effect, setEffect] = useState('');
  const [cause, setCause] = useState('');

  React.useEffect(() => {
    if (fmeaRow) {
      setComponent(fmeaRow.component_id || '');
      setFailureMode(fmeaRow.failure_mode || '');
      setEffect(fmeaRow.effect || '');
      setCause(fmeaRow.cause || '');
    }
  }, [fmeaRow]);

  const handleSuggest = async () => {
    if (!component || !failureMode || !effect || !cause) {
      setError('Please fill in all required fields: Component, Failure Mode, Effect, and Cause');
      return;
    }

    setLoading(true);
    setError(null);
    setSuggestions(null);

    try {
      const response = await aiApi.suggest({
        component,
        failure_mode: failureMode,
        effect,
        cause,
      });
      setSuggestions(response);
    } catch (err: any) {
      setError(err.message || 'Failed to get AI suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = () => {
    if (suggestions) {
      onApply(suggestions);
      setSuggestions(null);
      onClose();
    }
  };

  return (
    <Drawer anchor="right" open={open} onClose={onClose} PaperProps={{ sx: { width: 400, p: 3 } }}>
      <Box>
        <Typography variant="h6" gutterBottom>
          AI FMEA Suggestions
        </Typography>

        <TextField
          fullWidth
          label="Component"
          value={component}
          onChange={(e) => setComponent(e.target.value)}
          margin="normal"
          required
        />

        <TextField
          fullWidth
          label="Failure Mode"
          value={failureMode}
          onChange={(e) => setFailureMode(e.target.value)}
          margin="normal"
          required
          multiline
          rows={2}
        />

        <TextField
          fullWidth
          label="Effect"
          value={effect}
          onChange={(e) => setEffect(e.target.value)}
          margin="normal"
          required
          multiline
          rows={2}
        />

        <TextField
          fullWidth
          label="Cause"
          value={cause}
          onChange={(e) => setCause(e.target.value)}
          margin="normal"
          required
          multiline
          rows={2}
        />

        <Button
          variant="contained"
          fullWidth
          onClick={handleSuggest}
          disabled={loading || !component || !failureMode || !effect || !cause}
          sx={{ mt: 2, mb: 2 }}
        >
          {loading ? <CircularProgress size={24} /> : 'Get AI Suggestions'}
        </Button>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {suggestions && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              AI Suggestions:
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Severity: <Chip label={suggestions.severity} size="small" />
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Probability: <Chip label={suggestions.probability} size="small" />
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Detection: <Chip label={suggestions.detection} size="small" />
              </Typography>
              <Typography variant="body2" color="text.secondary">
                RPN: <Chip label={suggestions.rpn} size="small" color="primary" />
              </Typography>
            </Box>

            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Mitigation:</strong>
            </Typography>
            <Typography variant="body2" sx={{ mb: 2, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
              {suggestions.mitigation}
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Residual Severity: <Chip label={suggestions.residual_severity} size="small" />
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Residual Probability: <Chip label={suggestions.residual_probability} size="small" />
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Residual Detection: <Chip label={suggestions.residual_detection} size="small" />
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Residual RPN: <Chip label={suggestions.residual_rpn} size="small" color="secondary" />
              </Typography>
            </Box>

            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Financial Impact:</strong> ${suggestions.financial_impact.toLocaleString()}
            </Typography>

            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={handleApply}
              sx={{ mt: 2 }}
            >
              Apply Suggestions
            </Button>
          </Box>
        )}
      </Box>
    </Drawer>
  );
};

export default AiSidebar;

