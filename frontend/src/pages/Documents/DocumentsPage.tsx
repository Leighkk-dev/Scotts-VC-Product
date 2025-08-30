import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Tabs,
  Tab,
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
  DialogActions,
  Alert,
} from '@mui/material';
import {
  CloudUpload,
  Visibility,
  Download,
  Delete,
  Refresh,
} from '@mui/icons-material';

import DocumentUpload from '../../components/Documents/DocumentUpload';

interface Document {
  id: string;
  venture_id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  processing_status: string;
  document_type?: string;
  confidence_score?: number;
  text_quality?: number;
  created_at: string;
  processing_completed_at?: string;
}

const DocumentsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedVentureId, setSelectedVentureId] = useState('');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await fetch('/v1/documents/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadComplete = (documentId: string) => {
    // Refresh the documents list
    fetchDocuments();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'processing':
        return 'warning';
      case 'pending':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const filteredDocuments = documents.filter(doc => {
    switch (activeTab) {
      case 1: // Processing
        return ['pending', 'processing'].includes(doc.processing_status);
      case 2: // Completed
        return doc.processing_status === 'completed';
      case 3: // Failed
        return doc.processing_status === 'failed';
      default: // All
        return true;
    }
  });

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Documents
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchDocuments}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<CloudUpload />}
            onClick={() => setUploadDialogOpen(true)}
          >
            Upload Documents
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" component="div">
                {documents.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Documents
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" component="div">
                {documents.filter(d => d.processing_status === 'completed').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Processed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" component="div">
                {documents.filter(d => ['pending', 'processing'].includes(d.processing_status)).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Processing
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" component="div">
                {documents.filter(d => d.processing_status === 'failed').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Failed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Document List */}
      <Card>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab label={`All (${documents.length})`} />
              <Tab label={`Processing (${documents.filter(d => ['pending', 'processing'].includes(d.processing_status)).length})`} />
              <Tab label={`Completed (${documents.filter(d => d.processing_status === 'completed').length})`} />
              <Tab label={`Failed (${documents.filter(d => d.processing_status === 'failed').length})`} />
            </Tabs>
          </Box>

          {filteredDocuments.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                No documents found
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Upload your first document to get started with AI analysis
              </Typography>
              <Button
                variant="contained"
                startIcon={<CloudUpload />}
                onClick={() => setUploadDialogOpen(true)}
              >
                Upload Document
              </Button>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Document</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Quality</TableCell>
                    <TableCell>Uploaded</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredDocuments.map((document) => (
                    <TableRow key={document.id}>
                      <TableCell>
                        <Typography variant="subtitle2">
                          {document.original_filename}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {document.filename}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={document.document_type || 'Unknown'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{formatFileSize(document.file_size)}</TableCell>
                      <TableCell>
                        <Chip
                          label={document.processing_status}
                          size="small"
                          color={getStatusColor(document.processing_status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        {document.confidence_score && document.text_quality ? (
                          <Box>
                            <Typography variant="caption" display="block">
                              Confidence: {(document.confidence_score * 100).toFixed(0)}%
                            </Typography>
                            <Typography variant="caption" display="block">
                              Quality: {(document.text_quality * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        ) : (
                          <Typography variant="caption" color="text.secondary">
                            N/A
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatDate(document.created_at)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton size="small" title="View Details">
                            <Visibility />
                          </IconButton>
                          <IconButton size="small" title="Download">
                            <Download />
                          </IconButton>
                          <IconButton size="small" title="Delete" color="error">
                            <Delete />
                          </IconButton>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Upload Dialog */}
      <Dialog 
        open={uploadDialogOpen} 
        onClose={() => setUploadDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Upload Documents</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 3 }}>
            Upload pitch decks, financial models, business plans, and other documents for AI analysis.
            Supported formats: PDF, PowerPoint, Excel, Word (max 50MB each).
          </Alert>
          <DocumentUpload
            ventureId="temp-venture-id" // TODO: Get from selected venture
            onUploadComplete={handleUploadComplete}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentsPage;