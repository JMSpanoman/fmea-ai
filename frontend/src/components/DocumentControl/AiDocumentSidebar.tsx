import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Paper,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { aiPhase3Api } from '../../services/apiPhase3';
import { DocumentDraftRequest, DocumentDraftResponse } from '../../types';

interface AiDocumentSidebarProps {
  onDraftGenerated: (draft: string) => void;
  onClose: () => void;
}

const AiDocumentSidebar: React.FC<AiDocumentSidebarProps> = ({
  onDraftGenerated,
  onClose,
}) => {
  const [type, setType] = useState('sop');
  const [context, setContext] = useState('');
  const [requirements, setRequirements] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [draft, setDraft] = useState<DocumentDraftResponse | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const request: DocumentDraftRequest = {
        type,
        context: context || undefined,
        requirements: requirements
          ? requirements.split('\n').filter((r) => r.trim())
          : undefined,
      };

      const response = await aiPhase3Api.draftDocument(request);
      setDraft(response);
      onDraftGenerated(response.draft);
    } catch (error) {
      console.error('Error generating document:', error);
      alert('Failed to generate document draft');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Box sx={{ width: 400, p: 2, borderLeft: '1px solid #e0e0e0' }}>
      <Typography variant="h6" gutterBottom>
        AI Document Assistant
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 2 }}>
        <TextField
          select
          label="Document Type"
          value={type}
          onChange={(e) => setType(e.target.value)}
          fullWidth
          SelectProps={{ native: true }}
        >
          <option value="dhf">DHF</option>
          <option value="dmr">DMR</option>
          <option value="sop">SOP</option>
          <option value="form">Form</option>
          <option value="work_instruction">Work Instruction</option>
          <option value="record">Record</option>
        </TextField>

        <TextField
          label="Context"
          value={context}
          onChange={(e) => setContext(e.target.value)}
          multiline
          rows={3}
          fullWidth
          placeholder="Describe the document context..."
        />

        <TextField
          label="Requirements (one per line)"
          value={requirements}
          onChange={(e) => setRequirements(e.target.value)}
          multiline
          rows={4}
          fullWidth
          placeholder="Enter requirements, one per line..."
        />

        <Button
          variant="contained"
          onClick={handleGenerate}
          disabled={isGenerating}
          fullWidth
        >
          {isGenerating ? (
            <>
              <CircularProgress size={20} sx={{ mr: 1 }} />
              Generating...
            </>
          ) : (
            'Generate Document Draft'
          )}
        </Button>
      </Box>

      {draft && (
        <Paper sx={{ p: 2, mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Generated Draft:
          </Typography>
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
            {draft.draft.substring(0, 500)}...
          </Typography>
        </Paper>
      )}

      <Button variant="outlined" onClick={onClose} fullWidth sx={{ mt: 2 }}>
        Close
      </Button>
    </Box>
  );
};

export default AiDocumentSidebar;

