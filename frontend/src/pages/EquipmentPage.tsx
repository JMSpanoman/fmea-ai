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
import { Add, Build } from '@mui/icons-material';
import { Equipment, CalibrationRecord } from '../types';
import { equipmentApi } from '../services/apiPhase3';
import { useParams, useSearchParams } from 'react-router-dom';

const EquipmentPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [searchParams] = useSearchParams();
  const projectIdFromQuery = searchParams.get('projectId');
  const finalProjectId = projectId || projectIdFromQuery || '';
  
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showCalibrateDialog, setShowCalibrateDialog] = useState(false);
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);
  const [loading, setLoading] = useState(true);
  const [newEquipment, setNewEquipment] = useState({
    name: '',
    serial_number: '',
  });
  const [calibration, setCalibration] = useState({
    performed_at: new Date().toISOString().split('T')[0],
    result: '',
  });

  if (!finalProjectId) {
    return <Typography>Project ID required. Please select a project first.</Typography>;
  }

  useEffect(() => {
    if (finalProjectId) {
      loadEquipment();
    }
  }, [finalProjectId]);

  const loadEquipment = async () => {
    try {
      const equipmentList = await equipmentApi.getAll(finalProjectId);
      setEquipment(equipmentList);
    } catch (error) {
      console.error('Error loading equipment:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await equipmentApi.create(finalProjectId, {
        ...newEquipment,
        project_id: finalProjectId,
      });
      setShowCreateDialog(false);
      setNewEquipment({ name: '', serial_number: '' });
      loadEquipment();
    } catch (error) {
      console.error('Error creating equipment:', error);
      alert('Failed to create equipment');
    }
  };

  const handleCalibrate = async () => {
    if (!selectedEquipment) return;
    try {
      await equipmentApi.calibrate(finalProjectId, selectedEquipment.id, {
        ...calibration,
        performed_at: new Date(calibration.performed_at).toISOString(),
        equipment_id: selectedEquipment.id,
      });
      setShowCalibrateDialog(false);
      setSelectedEquipment(null);
      loadEquipment();
    } catch (error) {
      console.error('Error calibrating equipment:', error);
      alert('Failed to record calibration');
    }
  };

  const isCalibrationDue = (calibrationDue?: string) => {
    if (!calibrationDue) return false;
    const dueDate = new Date(calibrationDue);
    const today = new Date();
    return dueDate <= today;
  };

  if (loading) {
    return <Typography>Loading equipment...</Typography>;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Equipment & Calibration</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setShowCreateDialog(true)}
        >
          Add Equipment
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Serial Number</TableCell>
              <TableCell>Calibration Due</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {equipment.map((eq) => (
              <TableRow key={eq.id}>
                <TableCell>{eq.name}</TableCell>
                <TableCell>{eq.serial_number || 'N/A'}</TableCell>
                <TableCell>
                  {eq.calibration_due ? (
                    <Chip
                      label={new Date(eq.calibration_due).toLocaleDateString()}
                      color={isCalibrationDue(eq.calibration_due) ? 'error' : 'default'}
                      size="small"
                    />
                  ) : (
                    'N/A'
                  )}
                </TableCell>
                <TableCell>{eq.status || 'Active'}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => {
                      setSelectedEquipment(eq);
                      setShowCalibrateDialog(true);
                    }}
                    color="primary"
                  >
                    <Build />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={showCreateDialog} onClose={() => setShowCreateDialog(false)}>
        <DialogTitle>Add Equipment</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, p: 2, minWidth: 400 }}>
            <TextField
              label="Equipment Name"
              value={newEquipment.name}
              onChange={(e) => setNewEquipment({ ...newEquipment, name: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Serial Number"
              value={newEquipment.serial_number}
              onChange={(e) => setNewEquipment({ ...newEquipment, serial_number: e.target.value })}
              fullWidth
            />
            <Button variant="contained" onClick={handleCreate}>
              Create
            </Button>
          </Box>
        </DialogContent>
      </Dialog>

      <Dialog open={showCalibrateDialog} onClose={() => setShowCalibrateDialog(false)}>
        <DialogTitle>Record Calibration</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, p: 2, minWidth: 400 }}>
            <Typography variant="body2">
              Equipment: {selectedEquipment?.name}
            </Typography>
            <TextField
              label="Performed At"
              type="date"
              value={calibration.performed_at}
              onChange={(e) =>
                setCalibration({ ...calibration, performed_at: e.target.value })
              }
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Result"
              value={calibration.result}
              onChange={(e) => setCalibration({ ...calibration, result: e.target.value })}
              multiline
              rows={3}
              fullWidth
            />
            <Button variant="contained" onClick={handleCalibrate}>
              Record Calibration
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default EquipmentPage;

