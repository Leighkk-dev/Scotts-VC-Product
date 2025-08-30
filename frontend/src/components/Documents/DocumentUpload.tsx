import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
} from '@mui/material';
import {
  CloudUpload,
  Delete,
  InsertDriveFile,
  CheckCircle,
  Error,
  Schedule,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';

interface UploadFile {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  error?: string;
  documentId?: string;
}

interface DocumentUploadProps {
  ventureId: string;
  onUploadComplete?: (documentId: string) => void;
}

const SUPPORTED_TYPES = {
  'application/pdf': 'PDF',
  'application/vnd.ms-powerpoint': 'PowerPoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
  'application/vnd.ms-excel': 'Excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
  'application/msword': 'Word',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
};

const DOCUMENT_TYPES = [
  { value: 'pitch_deck', label: 'Pitch Deck' },
  { value: 'financial_model', label: 'Financial Model' },
  { value: 'business_plan', label: 'Business Plan' },
  { value: 'market_analysis', label: 'Market Analysis' },
  { value: 'technical_document', label: 'Technical Document' },
  { value: 'legal_document', label: 'Legal Document' },
  { value: 'other', label: 'Other' },
];

const DocumentUpload: React.FC<DocumentUploadProps> = ({ ventureId, onUploadComplete }) => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<UploadFile | null>(null);
  const [documentType, setDocumentType] = useState('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      status: 'pending' as const,
      progress: 0,
    }));

    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: SUPPORTED_TYPES,
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true,
  });

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const uploadFile = async (uploadFile: UploadFile, docType: string) => {
    const formData = new FormData();
    formData.append('file', uploadFile.file);
    formData.append('venture_id', ventureId);
    if (docType) {
      formData.append('document_type', docType);
    }

    try {
      // Update status to uploading
      setFiles(prev => prev.map(f => 
        f.id === uploadFile.id 
          ? { ...f, status: 'uploading', progress: 0 }
          : f
      ));

      const response = await fetch('/v1/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();

      // Update status to processing
      setFiles(prev => prev.map(f => 
        f.id === uploadFile.id 
          ? { 
              ...f, 
              status: 'processing', 
              progress: 100,
              documentId: result.id 
            }
          : f
      ));

      // Start polling for processing status
      pollProcessingStatus(uploadFile.id, result.id);

    } catch (error) {
      setFiles(prev => prev.map(f => 
        f.id === uploadFile.id 
          ? { 
              ...f, 
              status: 'error', 
              error: error instanceof Error ? error.message : 'Upload failed' 
            }
          : f
      ));
    }
  };

  const pollProcessingStatus = async (fileId: string, documentId: string) => {
    const maxAttempts = 60; // 5 minutes with 5-second intervals
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`/v1/documents/${documentId}/status`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to get processing status');
        }

        const status = await response.json();

        if (status.status === 'completed') {
          setFiles(prev => prev.map(f => 
            f.id === fileId 
              ? { ...f, status: 'completed' }
              : f
          ));
          onUploadComplete?.(documentId);
          return;
        }

        if (status.status === 'failed') {
          setFiles(prev => prev.map(f => 
            f.id === fileId 
              ? { 
                  ...f, 
                  status: 'error', 
                  error: status.error || 'Processing failed' 
                }
              : f
          ));
          return;
        }

        // Continue polling if still processing
        if (status.status === 'processing' && attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 5000); // Poll every 5 seconds
        }

      } catch (error) {
        setFiles(prev => prev.map(f => 
          f.id === fileId 
            ? { 
                ...f, 
                status: 'error', 
                error: 'Failed to check processing status' 
              }
            : f
        ));
      }
    };

    // Start polling after a short delay
    setTimeout(poll, 2000);
  };

  const handleUploadClick = (file: UploadFile) => {
    setSelectedFile(file);
    setDocumentType('');
    setDialogOpen(true);
  };

  const handleUploadConfirm = () => {
    if (selectedFile) {
      uploadFile(selectedFile, documentType);
      setDialogOpen(false);
      setSelectedFile(null);
    }
  };

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'error':
        return <Error color="error" />;
      case 'processing':
      case 'uploading':
        return <Schedule color="warning" />;
      default:
        return <InsertDriveFile />;
    }
  };

  const getStatusColor = (status: UploadFile['status']) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'error':
        return 'error';
      case 'processing':
        return 'warning';
      case 'uploading':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* Drag and Drop Area */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          textAlign: 'center',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          backgroundColor: isDragActive ? 'primary.light' : 'background.paper',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'primary.light',
          },
        }}
      >
        <input {...getInputProps()} />
        <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          or click to browse files
        </Typography>
        <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
          {Object.values(SUPPORTED_TYPES).map((type, index) => (
            <Chip key={index} label={type} size="small" variant="outlined" />
          ))}
        </Box>
        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
          Maximum file size: 50MB
        </Typography>
      </Paper>

      {/* File List */}
      {files.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Files ({files.length})
          </Typography>
          <List>
            {files.map((file) => (
              <ListItem key={file.id} divider>
                <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                  {getStatusIcon(file.status)}
                </Box>
                <ListItemText
                  primary={file.file.name}
                  secondary={
                    <Box>
                      <Typography variant="caption" display="block">
                        {(file.file.size / 1024 / 1024).toFixed(2)} MB • {SUPPORTED_TYPES[file.file.type as keyof typeof SUPPORTED_TYPES]}
                      </Typography>
                      {file.status === 'uploading' && (
                        <LinearProgress 
                          variant="determinate" 
                          value={file.progress} 
                          sx={{ mt: 1, width: 200 }} 
                        />
                      )}
                      {file.status === 'processing' && (
                        <LinearProgress sx={{ mt: 1, width: 200 }} />
                      )}
                      {file.error && (
                        <Alert severity="error" sx={{ mt: 1 }}>
                          {file.error}
                        </Alert>
                      )}
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip 
                      label={file.status} 
                      size="small" 
                      color={getStatusColor(file.status) as any}
                      variant="outlined"
                    />
                    {file.status === 'pending' && (
                      <Button
                        size="small"
                        variant="contained"
                        onClick={() => handleUploadClick(file)}
                      >
                        Upload
                      </Button>
                    )}
                    <IconButton
                      edge="end"
                      onClick={() => removeFile(file.id)}
                      disabled={file.status === 'uploading' || file.status === 'processing'}
                    >
                      <Delete />
                    </IconButton>
                  </Box>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Upload Confirmation Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Document</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Please specify the document type to help with analysis:
          </Typography>
          <TextField
            select
            fullWidth
            label="Document Type"
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value)}
            sx={{ mt: 2 }}
          >
            {DOCUMENT_TYPES.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>
          {selectedFile && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="subtitle2">File Details:</Typography>
              <Typography variant="body2">Name: {selectedFile.file.name}</Typography>
              <Typography variant="body2">
                Size: {(selectedFile.file.size / 1024 / 1024).toFixed(2)} MB
              </Typography>
              <Typography variant="body2">
                Type: {SUPPORTED_TYPES[selectedFile.file.type as keyof typeof SUPPORTED_TYPES]}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleUploadConfirm} 
            variant="contained"
            disabled={!documentType}
          >
            Upload & Process
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentUpload;
