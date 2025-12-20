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
import { Add, Assessment } from '@mui/icons-material';
import { Supplier } from '../types';
import { suppliersApi, aiPhase3Api } from '../services/apiPhase3';
import { useParams, useSearchParams } from 'react-router-dom';

const SupplierQualityPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [searchParams] = useSearchParams();
  const projectIdFromQuery = searchParams.get('projectId');
  const finalProjectId = projectId || projectIdFromQuery || '';
  
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newSupplier, setNewSupplier] = useState({
    name: '',
    category: '',
    risk_rating: 5,
  });

  if (!finalProjectId) {
    return <Typography>Project ID required. Please select a project first.</Typography>;
  }

  useEffect(() => {
    if (finalProjectId) {
      loadSuppliers();
    }
  }, [finalProjectId]);

  const loadSuppliers = async () => {
    try {
      const supplierList = await suppliersApi.getAll(finalProjectId);
      setSuppliers(supplierList);
    } catch (error) {
      console.error('Error loading suppliers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await suppliersApi.create(finalProjectId, {
        ...newSupplier,
        project_id: finalProjectId,
      });
      setShowCreateDialog(false);
      setNewSupplier({ name: '', category: '', risk_rating: 5 });
      loadSuppliers();
    } catch (error) {
      console.error('Error creating supplier:', error);
      alert('Failed to create supplier');
    }
  };

  const handleAssessRisk = async (supplierId: string) => {
    try {
      const assessment = await aiPhase3Api.assessSupplierRisk({ supplier_id: supplierId });
      alert(`Risk Assessment:\nRating: ${assessment.risk_rating}\nConcerns: ${assessment.concerns.length}\nActions: ${assessment.recommended_actions.length}`);
    } catch (error) {
      console.error('Error assessing supplier risk:', error);
      alert('Failed to assess supplier risk');
    }
  };

  if (loading) {
    return <Typography>Loading suppliers...</Typography>;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Supplier Quality</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setShowCreateDialog(true)}
        >
          Add Supplier
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Risk Rating</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {suppliers.map((supplier) => (
              <TableRow key={supplier.id}>
                <TableCell>{supplier.name}</TableCell>
                <TableCell>{supplier.category || 'N/A'}</TableCell>
                <TableCell>
                  <Chip
                    label={supplier.risk_rating || 'N/A'}
                    color={supplier.risk_rating && supplier.risk_rating > 7 ? 'error' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{supplier.status || 'Active'}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleAssessRisk(supplier.id)}
                    color="primary"
                  >
                    <Assessment />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={showCreateDialog} onClose={() => setShowCreateDialog(false)}>
        <DialogTitle>Add Supplier</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, p: 2, minWidth: 400 }}>
            <TextField
              label="Supplier Name"
              value={newSupplier.name}
              onChange={(e) => setNewSupplier({ ...newSupplier, name: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Category"
              value={newSupplier.category}
              onChange={(e) => setNewSupplier({ ...newSupplier, category: e.target.value })}
              fullWidth
            />
            <TextField
              label="Risk Rating"
              type="number"
              value={newSupplier.risk_rating}
              onChange={(e) =>
                setNewSupplier({ ...newSupplier, risk_rating: parseInt(e.target.value) || 5 })
              }
              fullWidth
              inputProps={{ min: 1, max: 10 }}
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

export default SupplierQualityPage;

