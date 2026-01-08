import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Container,
  Dialog,
  DialogTitle,
  DialogContent,
} from '@mui/material';
import { Add } from '@mui/icons-material';
import DocumentList from '../components/DocumentControl/DocumentList';
import DocumentEditor from '../components/DocumentControl/DocumentEditor';
import AiDocumentSidebar from '../components/DocumentControl/AiDocumentSidebar';
import { Document } from '../types';
import { useParams, useSearchParams } from 'react-router-dom';

const DocumentControlPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [searchParams] = useSearchParams();
  const projectIdFromQuery = searchParams.get('projectId');
  const finalProjectId = projectId || projectIdFromQuery || '';
  
  const [documents, setDocuments] = useState<Document[]>([]);
  const [editingDocument, setEditingDocument] = useState<Document | undefined>();
  const [showEditor, setShowEditor] = useState(false);
  const [showAiSidebar, setShowAiSidebar] = useState(false);

  if (!finalProjectId) {
    return <Typography>Project ID required. Please select a project first.</Typography>;
  }

  const handleCreate = () => {
    setEditingDocument(undefined);
    setShowEditor(true);
  };

  const handleEdit = (document: Document) => {
    setEditingDocument(document);
    setShowEditor(true);
  };

  const handleSave = (document: Document) => {
    setShowEditor(false);
    setEditingDocument(undefined);
    // Reload documents
    window.location.reload();
  };

  const handleDraftGenerated = (draft: string) => {
    setShowAiSidebar(false);
    setEditingDocument({
      id: '',
      project_id: finalProjectId,
      name: 'AI Generated Document',
      type: 'sop',
      content: draft,
      version: 1,
      status: 'draft',
      created_at: new Date().toISOString(),
    });
    setShowEditor(true);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Document Control</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            onClick={() => setShowAiSidebar(true)}
          >
            AI Assistant
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreate}
          >
            Create Document
          </Button>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', gap: 2 }}>
        <Box sx={{ flex: 1 }}>
          <DocumentList
            projectId={finalProjectId}
            onEdit={handleEdit}
            onView={(doc) => {
              setEditingDocument(doc);
              setShowEditor(true);
            }}
          />
        </Box>

        {showAiSidebar && (
          <AiDocumentSidebar
            onDraftGenerated={handleDraftGenerated}
            onClose={() => setShowAiSidebar(false)}
          />
        )}
      </Box>

      <Dialog
        open={showEditor}
        onClose={() => setShowEditor(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingDocument ? 'Edit Document' : 'Create Document'}
        </DialogTitle>
        <DialogContent>
          <DocumentEditor
            projectId={finalProjectId}
            document={editingDocument}
            onSave={handleSave}
            onCancel={() => setShowEditor(false)}
          />
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default DocumentControlPage;

