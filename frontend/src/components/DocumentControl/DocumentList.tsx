import React, { useState, useEffect } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  IconButton,
  Typography,
  Chip,
} from '@mui/material';
import { Edit, Delete, Visibility, CheckCircle } from '@mui/icons-material';
import { Document } from '../../types';
import { documentsApi } from '../../services/apiPhase3';

interface DocumentListProps {
  projectId: string;
  onEdit?: (document: Document) => void;
  onView?: (document: Document) => void;
}

const DocumentList: React.FC<DocumentListProps> = ({
  projectId,
  onEdit,
  onView,
}) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDocuments();
  }, [projectId]);

  const loadDocuments = async () => {
    try {
      const docs = await documentsApi.getAll(projectId);
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (document: Document) => {
    try {
      await documentsApi.approve(projectId, document.id);
      loadDocuments();
    } catch (error) {
      console.error('Error approving document:', error);
      alert('Failed to approve document');
    }
  };

  const getStatusColor = (status: Document['status']) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'in_review':
        return 'warning';
      case 'draft':
        return 'default';
      case 'obsolete':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return <Typography>Loading documents...</Typography>;
  }

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Version</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {documents.map((doc) => (
            <TableRow key={doc.id}>
              <TableCell>{doc.name}</TableCell>
              <TableCell>{doc.type.toUpperCase()}</TableCell>
              <TableCell>{doc.version}</TableCell>
              <TableCell>
                <Chip
                  label={doc.status}
                  color={getStatusColor(doc.status) as any}
                  size="small"
                />
              </TableCell>
              <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
              <TableCell>
                <IconButton size="small" onClick={() => onView?.(doc)}>
                  <Visibility />
                </IconButton>
                <IconButton size="small" onClick={() => onEdit?.(doc)}>
                  <Edit />
                </IconButton>
                {doc.status !== 'approved' && (
                  <IconButton
                    size="small"
                    onClick={() => handleApprove(doc)}
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
  );
};

export default DocumentList;

