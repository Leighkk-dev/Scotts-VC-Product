import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const SettingsPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Application Settings
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This page will contain user and organization settings.
            Features coming in Phase 4:
          </Typography>
          <Box component="ul" sx={{ mt: 2 }}>
            <li>User profile management</li>
            <li>Organization settings</li>
            <li>Notification preferences</li>
            <li>Security settings</li>
            <li>API key management</li>
            <li>Billing and subscription</li>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SettingsPage;
