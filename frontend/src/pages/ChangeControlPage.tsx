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
} from '@mui/material';
import { Add, Edit, CheckCircle } from '@mui/icons-material';
import { ChangeControl } from '../types';
import { changeControlsApi, aiPhase3Api } from '../services/apiPhase3';
import ChangeControlForm from '../components/ChangeControl/ChangeControlForm';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '../contexts/ProjectContext';
import { UpstreamLinksPanel } from '../components/Traceability/UpstreamLinksPanel';

const ChangeControlPage: React.FC = () => {
  const { projectId, changeId } = useParams<{ projectId?: string; changeId?: string }>();
  const { currentProject } = useProject();
  const navigate = useNavigate();
  const finalProjectId = projectId || currentProject?.id || '';
  const [changeControls, setChangeControls] = useState<ChangeControl[]>([]);
  const [editingChange, setEditingChange] = useState<ChangeControl | undefined>();
  const [showEditor, setShowEditor] = useState(false);
  const [loading, setLoading] = useState(true);

  if (!projectId) {
    return <Typography>Project ID required</Typography>;
  }

  useEffect(() => {
    if (finalProjectId) {
      loadChangeControls();
    }
  }, [finalProjectId]);

  const loadChangeControls = async () => {
    try {
      const changes = await changeControlsApi.getAll(finalProjectId);
      setChangeControls(changes);
    } catch (error) {
      console.error('Error loading change controls:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (changeId: string) => {
    try {
      await changeControlsApi.approve(finalProjectId, changeId);
      loadChangeControls();
    } catch (error) {
      console.error('Error approving change control:', error);
      alert('Failed to approve change control');
    }
  };

  const handleAnalyzeImpact = async (changeId: string) => {
    try {
      const impact = await aiPhase3Api.analyzeChangeImpact({ change_control_id: changeId });
      alert(`Impact Analysis:\nAffected Risks: ${impact.affected_risks.length}\nAffected Design Inputs: ${impact.affected_design_inputs.length}`);
    } catch (error) {
      console.error('Error analyzing impact:', error);
      alert('Failed to analyze change impact');
    }
  };

  const getStatusColor = (status: ChangeControl['status']) => {
    switch (status) {
      case 'closed':
        return 'success';
      case 'approved':
        return 'info';
      case 'in_review':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading) {
    return <Typography>Loading change controls...</Typography>;
  }

  return (
    <Container maxWidth="xl">
      {/* Upstream Links Panel - Show if viewing a specific Change Control */}
      {changeId && finalProjectId && (
        <Box sx={{ mb: 3 }}>
          <UpstreamLinksPanel
            projectId={finalProjectId}
            artifactType="change_control"
            artifactId={changeId}
            onNavigate={(route) => navigate(route)}
          />
        </Box>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Change Control</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => {
            setEditingChange(undefined);
            setShowEditor(true);
          }}
        >
          Create Change Control
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {changeControls.map((cc) => (
              <TableRow key={cc.id}>
                <TableCell>{cc.title}</TableCell>
                <TableCell>
                  <Chip
                    label={cc.status}
                    color={getStatusColor(cc.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{new Date(cc.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <IconButton size="small" onClick={() => handleAnalyzeImpact(cc.id)}>
                    Analyze Impact
                  </IconButton>
                  {cc.status !== 'approved' && cc.status !== 'closed' && (
                    <IconButton
                      size="small"
                      onClick={() => handleApprove(cc.id)}
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

      <Dialog
        open={showEditor}
        onClose={() => setShowEditor(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingChange ? 'Edit Change Control' : 'Create Change Control'}
        </DialogTitle>
        <DialogContent>
          <ChangeControlForm
            projectId={finalProjectId}
            changeControl={editingChange}
            onSave={(cc) => {
              setShowEditor(false);
              loadChangeControls();
            }}
            onCancel={() => setShowEditor(false)}
          />
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default ChangeControlPage;
