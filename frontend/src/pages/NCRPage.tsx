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
} from '@mui/material';
import { Add, Psychology, CheckCircle } from '@mui/icons-material';
import { NCR } from '../types';
import { ncrsApi, aiPhase3Api } from '../services/apiPhase3';
import { useParams, useSearchParams } from 'react-router-dom';

const NCRPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [searchParams] = useSearchParams();
  const projectIdFromQuery = searchParams.get('projectId');
  const finalProjectId = projectId || projectIdFromQuery || '';
  
  const [ncrs, setNcrs] = useState<NCR[]>([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newNCR, setNewNCR] = useState({
    description: '',
    status: 'open',
  });

  if (!finalProjectId) {
    return <Typography>Project ID required. Please select a project first.</Typography>;
  }

  useEffect(() => {
    if (finalProjectId) {
      loadNCRs();
    }
  }, [finalProjectId]);

  const loadNCRs = async () => {
    try {
      const ncrList = await ncrsApi.getAll(finalProjectId);
      setNCRs(ncrList);
    } catch (error) {
      console.error('Error loading NCRs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await ncrsApi.create(finalProjectId, {
        ...newNCR,
        project_id: finalProjectId,
      });
      setShowCreateDialog(false);
      setNewNCR({ description: '', status: 'open' });
      loadNCRs();
    } catch (error) {
      console.error('Error creating NCR:', error);
      alert('Failed to create NCR');
    }
  };

  const handleAnalyze = async (ncrId: string) => {
    try {
      const analysis = await aiPhase3Api.analyzeNCR({ ncr_id: ncrId });
      alert(`NCR Analysis:\nRoot Cause: ${analysis.root_cause.substring(0, 100)}...\nCorrective Action: ${analysis.corrective_action.substring(0, 100)}...`);
    } catch (error) {
      console.error('Error analyzing NCR:', error);
      alert('Failed to analyze NCR');
    }
  };

  const handleClose = async (ncrId: string) => {
    try {
      await ncrsApi.close(finalProjectId, ncrId);
      loadNCRs();
    } catch (error) {
      console.error('Error closing NCR:', error);
      alert('Failed to close NCR');
    }
  };

  if (loading) {
    return <Typography>Loading NCRs...</Typography>;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Nonconformance (NCR)</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setShowCreateDialog(true)}
        >
          Create NCR
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Description</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {ncrs.map((ncr) => (
              <TableRow key={ncr.id}>
                <TableCell>{ncr.description.substring(0, 100)}...</TableCell>
                <TableCell>
                  <Chip label={ncr.status} size="small" />
                </TableCell>
                <TableCell>{new Date(ncr.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleAnalyze(ncr.id)}
                    color="primary"
                  >
                    <Psychology />
                  </IconButton>
                  {ncr.status !== 'closed' && (
                    <IconButton
                      size="small"
                      onClick={() => handleClose(ncr.id)}
                      color="success"
                    >
                      <CheckCircle />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={showCreateDialog} onClose={() => setShowCreateDialog(false)}>
        <DialogTitle>Create NCR</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, p: 2, minWidth: 500 }}>
            <TextField
              label="Description"
              value={newNCR.description}
              onChange={(e) => setNewNCR({ ...newNCR, description: e.target.value })}
              multiline
              rows={4}
              fullWidth
              required
            />
            <Button variant="contained" onClick={handleCreate}>
              Create
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default NCRPage;

