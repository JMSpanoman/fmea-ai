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
import { ChangeControl } from '../../types';
import { changeControlsApi } from '../../services/apiPhase3';

interface ChangeControlFormProps {
  projectId: string;
  changeControl?: ChangeControl;
  onSave: (changeControl: ChangeControl) => void;
  onCancel: () => void;
}

const ChangeControlForm: React.FC<ChangeControlFormProps> = ({
  projectId,
  changeControl,
  onSave,
  onCancel,
}) => {
  const [title, setTitle] = useState(changeControl?.title || '');
  const [description, setDescription] = useState(changeControl?.description || '');
  const [reason, setReason] = useState(changeControl?.reason || '');
  const [status, setStatus] = useState<ChangeControl['status']>(
    changeControl?.status || 'open'
  );
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const ccData = {
        title,
        description,
        reason,
        status,
        project_id: projectId,
      };

      let savedChangeControl: ChangeControl;
      if (changeControl) {
        savedChangeControl = await changeControlsApi.update(
          projectId,
          changeControl.id,
          ccData
        );
      } else {
        savedChangeControl = await changeControlsApi.create(projectId, ccData);
      }

      onSave(savedChangeControl);
    } catch (error) {
      console.error('Error saving change control:', error);
      alert('Failed to save change control');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {changeControl ? 'Edit Change Control' : 'Create Change Control'}
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField
          label="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          fullWidth
          required
        />

        <TextField
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          multiline
          rows={4}
          fullWidth
        />

        <TextField
          label="Reason"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          multiline
          rows={3}
          fullWidth
        />

        <FormControl fullWidth>
          <InputLabel>Status</InputLabel>
          <Select
            value={status}
            onChange={(e) => setStatus(e.target.value as ChangeControl['status'])}
            label="Status"
          >
            <MenuItem value="open">Open</MenuItem>
            <MenuItem value="in_review">In Review</MenuItem>
            <MenuItem value="approved">Approved</MenuItem>
            <MenuItem value="implemented">Implemented</MenuItem>
            <MenuItem value="verified">Verified</MenuItem>
            <MenuItem value="closed">Closed</MenuItem>
          </Select>
        </FormControl>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button variant="outlined" onClick={onCancel}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={isSaving || !title}
          >
            {isSaving ? 'Saving...' : 'Save'}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default ChangeControlForm;

