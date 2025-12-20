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
} from '@mui/material';
import { TrainingRecord } from '../types';
import { trainingApi } from '../services/apiPhase3';
import { useAuth } from '../contexts/AuthContext';

const TrainingPage: React.FC = () => {
  const { user } = useAuth();
  const [trainingRecords, setTrainingRecords] = useState<TrainingRecord[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Get user ID from localStorage or context
  const userId = (user as any)?.id || localStorage.getItem('userId') || '';

  useEffect(() => {
    if (userId) {
      loadTraining();
    }
  }, [userId]);

  const loadTraining = async () => {
    if (!userId) return;
    try {
      const records = await trainingApi.getUserTraining(userId);
      setTrainingRecords(records);
    } catch (error) {
      console.error('Error loading training records:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (recordId: string) => {
    if (!userId) return;
    try {
      await trainingApi.complete(userId, recordId);
      loadTraining();
    } catch (error) {
      console.error('Error completing training:', error);
      alert('Failed to complete training');
    }
  };

  const getStatusColor = (status: TrainingRecord['status']) => {
    switch (status) {
      case 'complete':
        return 'success';
      case 'in_progress':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading) {
    return <Typography>Loading training records...</Typography>;
  }

  if (!user) {
    return <Typography>Please log in to view training records</Typography>;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4">Training & Competency</Typography>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Document ID</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Assigned</TableCell>
              <TableCell>Completed</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {trainingRecords.map((record) => (
              <TableRow key={record.id}>
                <TableCell>{record.document_id}</TableCell>
                <TableCell>
                  <Chip
                    label={record.status}
                    color={getStatusColor(record.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{new Date(record.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  {record.completed_at
                    ? new Date(record.completed_at).toLocaleDateString()
                    : 'N/A'}
                </TableCell>
                <TableCell>
                  {record.status !== 'complete' && (
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => handleComplete(record.id)}
                    >
                      Mark Complete
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default TrainingPage;

