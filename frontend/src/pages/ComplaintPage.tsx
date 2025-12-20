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
import { Add, Search } from '@mui/icons-material';
import { Complaint } from '../types';
import { complaintsApi, aiPhase3Api } from '../services/apiPhase3';
import { useParams, useSearchParams } from 'react-router-dom';

const ComplaintPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [searchParams] = useSearchParams();
  const projectIdFromQuery = searchParams.get('projectId');
  const finalProjectId = projectId || projectIdFromQuery || '';
  
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newComplaint, setNewComplaint] = useState({
    description: '',
  });

  if (!finalProjectId) {
    return <Typography>Project ID required. Please select a project first.</Typography>;
  }

  useEffect(() => {
    if (finalProjectId) {
      loadComplaints();
    }
  }, [finalProjectId]);

  const loadComplaints = async () => {
    try {
      const complaintList = await complaintsApi.getAll(finalProjectId);
      setComplaints(complaintList);
    } catch (error) {
      console.error('Error loading complaints:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await complaintsApi.create(finalProjectId, {
        ...newComplaint,
        project_id: finalProjectId,
      });
      setShowCreateDialog(false);
      setNewComplaint({ description: '' });
      loadComplaints();
    } catch (error) {
      console.error('Error creating complaint:', error);
      alert('Failed to create complaint');
    }
  };

  const handleInvestigate = async (complaintId: string) => {
    try {
      const investigation = await aiPhase3Api.investigateComplaint({ complaint_id: complaintId });
      alert(`Investigation:\n${investigation.investigation.substring(0, 200)}...\nReportability: ${investigation.reportability_decision}`);
    } catch (error) {
      console.error('Error investigating complaint:', error);
      alert('Failed to investigate complaint');
    }
  };

  if (loading) {
    return <Typography>Loading complaints...</Typography>;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Complaint Handling</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setShowCreateDialog(true)}
        >
          Create Complaint
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Description</TableCell>
              <TableCell>Reportability</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {complaints.map((complaint) => (
              <TableRow key={complaint.id}>
                <TableCell>{complaint.description.substring(0, 100)}...</TableCell>
                <TableCell>
                  <Chip
                    label={complaint.reportability || 'Pending'}
                    color={complaint.reportability === 'reportable' ? 'error' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{new Date(complaint.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleInvestigate(complaint.id)}
                    color="primary"
                  >
                    <Search />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={showCreateDialog} onClose={() => setShowCreateDialog(false)}>
        <DialogTitle>Create Complaint</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, p: 2, minWidth: 500 }}>
            <TextField
              label="Description"
              value={newComplaint.description}
              onChange={(e) => setNewComplaint({ ...newComplaint, description: e.target.value })}
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

export default ComplaintPage;

