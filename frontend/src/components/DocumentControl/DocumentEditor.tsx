import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Paper,
} from '@mui/material';
import { Document } from '../../types';
import { documentsApi } from '../../services/apiPhase3';

interface DocumentEditorProps {
  projectId: string;
  document?: Document;
  onSave: (document: Document) => void;
  onCancel: () => void;
}

const DocumentEditor: React.FC<DocumentEditorProps> = ({
  projectId,
  document,
  onSave,
  onCancel,
}) => {
  const [name, setName] = useState(document?.name || '');
  const [type, setType] = useState<Document['type']>(document?.type || 'sop');
  const [content, setContent] = useState(document?.content || '');
  const [status, setStatus] = useState<Document['status']>(document?.status || 'draft');
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const docData = {
        name,
        type,
        content,
        status,
        project_id: projectId,
      };

      let savedDocument: Document;
      if (document) {
        savedDocument = await documentsApi.update(projectId, document.id, docData);
      } else {
        savedDocument = await documentsApi.create(projectId, docData);
      }

      onSave(savedDocument);
    } catch (error) {
      console.error('Error saving document:', error);
      alert('Failed to save document');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {document ? 'Edit Document' : 'Create Document'}
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField
          label="Document Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          fullWidth
          required
        />

        <FormControl fullWidth>
          <InputLabel>Document Type</InputLabel>
          <Select
            value={type}
            onChange={(e) => setType(e.target.value as Document['type'])}
            label="Document Type"
          >
            <MenuItem value="dhf">DHF</MenuItem>
            <MenuItem value="dmr">DMR</MenuItem>
            <MenuItem value="sop">SOP</MenuItem>
            <MenuItem value="form">Form</MenuItem>
            <MenuItem value="work_instruction">Work Instruction</MenuItem>
            <MenuItem value="record">Record</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>Status</InputLabel>
          <Select
            value={status}
            onChange={(e) => setStatus(e.target.value as Document['status'])}
            label="Status"
          >
            <MenuItem value="draft">Draft</MenuItem>
            <MenuItem value="in_review">In Review</MenuItem>
            <MenuItem value="approved">Approved</MenuItem>
            <MenuItem value="obsolete">Obsolete</MenuItem>
          </Select>
        </FormControl>

        <TextField
          label="Content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          multiline
          rows={10}
          fullWidth
        />

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button variant="outlined" onClick={onCancel}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={isSaving || !name}
          >
            {isSaving ? 'Saving...' : 'Save'}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default DocumentEditor;

