import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { Add, Close } from '@mui/icons-material';
import { Audit } from '../types';
import { auditsApi, aiPhase3Api } from '../services/apiPhase3';
import { useParams, useSearchParams } from 'react-router-dom';

const AuditPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [searchParams] = useSearchParams();
  const projectIdFromQuery = searchParams.get('projectId');
  const finalProjectId = projectId || projectIdFromQuery || '';
  
  const [audits, setAudits] = useState<Audit[]>([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showPrepareDialog, setShowPrepareDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newAudit, setNewAudit] = useState({
    type: 'internal' as Audit['type'],
    scope: '',
    status: 'planned',
  });

  if (!finalProjectId) {
    return <Typography>Project ID required. Please select a project first.</Typography>;
  }

  useEffect(() => {
    if (finalProjectId) {
      loadAudits();
    }
  }, [finalProjectId]);

  const loadAudits = async () => {
    try {
      const auditList = await auditsApi.getAll(finalProjectId);
      setAudits(auditList);
    } catch (error) {
      console.error('Error loading audits:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await auditsApi.create(finalProjectId, {
        ...newAudit,
        project_id: finalProjectId,
      });
      setShowCreateDialog(false);
      loadAudits();
    } catch (error) {
      console.error('Error creating audit:', error);
      alert('Failed to create audit');
    }
  };

  const handlePrepare = async () => {
    try {
      const preparation = await aiPhase3Api.prepareAudit({
        project_id: finalProjectId,
        audit_type: newAudit.type,
      });
      alert(`Audit Preparation:\nChecklist Items: ${preparation.checklist.length}\nGaps: ${preparation.gaps.length}\nRisk Areas: ${preparation.risk_areas.length}`);
      setShowPrepareDialog(false);
    } catch (error) {
      console.error('Error preparing audit:', error);
      alert('Failed to prepare audit');
    }
  };

  const handleClose = async (auditId: string) => {
    try {
      await auditsApi.close(finalProjectId, auditId);
      loadAudits();
    } catch (error) {
      console.error('Error closing audit:', error);
      alert('Failed to close audit');
    }
  };

  if (loading) {
    return <Typography>Loading audits...</Typography>;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Audit Management</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            onClick={() => setShowPrepareDialog(true)}
          >
            AI Prepare Audit
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setShowCreateDialog(true)}
          >
            Create Audit
          </Button>
        </Box>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Type</TableCell>
              <TableCell>Scope</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Scheduled Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {audits.map((audit) => (
              <TableRow key={audit.id}>
                <TableCell>{audit.type}</TableCell>
                <TableCell>{audit.scope || 'N/A'}</TableCell>
                <TableCell>
                  <Chip label={audit.status} size="small" />
                </TableCell>
                <TableCell>
                  {audit.scheduled_date
                    ? new Date(audit.scheduled_date).toLocaleDateString()
                    : 'N/A'}
                </TableCell>
                <TableCell>
                  {audit.status !== 'closed' && (
                    <IconButton
                      size="small"
                      onClick={() => handleClose(audit.id)}
                      color="success"
                    >
                      <Close />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={showCreateDialog} onClose={() => setShowCreateDialog(false)}>
        <DialogTitle>Create Audit</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, p: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select
                value={newAudit.type}
                onChange={(e) =>
                  setNewAudit({ ...newAudit, type: e.target.value as Audit['type'] })
                }
              >
                <MenuItem value="internal">Internal</MenuItem>
                <MenuItem value="supplier">Supplier</MenuItem>
                <MenuItem value="external">External</MenuItem>
                <MenuItem value="regulatory">Regulatory</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Scope"
              value={newAudit.scope}
              onChange={(e) => setNewAudit({ ...newAudit, scope: e.target.value })}
              multiline
              rows={3}
            />
            <Button variant="contained" onClick={handleCreate}>
              Create
            </Button>
          </Box>
        </DialogContent>
      </Dialog>

      <Dialog open={showPrepareDialog} onClose={() => setShowPrepareDialog(false)}>
        <DialogTitle>AI Audit Preparation</DialogTitle>
        <DialogContent>
          <Box sx={{ p: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Audit Type</InputLabel>
              <Select
                value={newAudit.type}
                onChange={(e) =>
                  setNewAudit({ ...newAudit, type: e.target.value as Audit['type'] })
                }
              >
                <MenuItem value="internal">Internal</MenuItem>
                <MenuItem value="supplier">Supplier</MenuItem>
                <MenuItem value="external">External</MenuItem>
                <MenuItem value="regulatory">Regulatory</MenuItem>
              </Select>
            </FormControl>
            <Button variant="contained" onClick={handlePrepare} fullWidth>
              Generate Audit Preparation
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default AuditPage;

