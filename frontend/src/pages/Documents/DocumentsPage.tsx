import React from 'react';
import { Box, Typography, Card, CardContent, Button } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

const DocumentsPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Documents
        </Typography>
        <Button variant="contained" startIcon={<CloudUpload />}>
          Upload Document
        </Button>
      </Box>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Document Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This page will handle document uploads and management.
            Features coming in Phase 2:
          </Typography>
          <Box component="ul" sx={{ mt: 2 }}>
            <li>Drag-and-drop file upload</li>
            <li>Support for PDF, PPT, Excel, Word documents</li>
            <li>Document processing status tracking</li>
            <li>File organization and categorization</li>
            <li>Document viewer and annotation</li>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DocumentsPage;
