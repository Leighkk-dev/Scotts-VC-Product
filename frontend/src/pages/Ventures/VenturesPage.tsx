import React from 'react';
import { Box, Typography, Card, CardContent, Button } from '@mui/material';
import { Add } from '@mui/icons-material';

const VenturesPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Ventures
        </Typography>
        <Button variant="contained" startIcon={<Add />}>
          Add Venture
        </Button>
      </Box>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Investment Opportunities
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This page will display all investment ventures and opportunities.
            Features coming in Phase 2:
          </Typography>
          <Box component="ul" sx={{ mt: 2 }}>
            <li>Venture listing with filtering and search</li>
            <li>Venture details and profiles</li>
            <li>Investment tracking and status</li>
            <li>Portfolio management</li>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default VenturesPage;
