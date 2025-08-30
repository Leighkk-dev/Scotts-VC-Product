import React from 'react';
import { Box, Typography, Card, CardContent, Button } from '@mui/material';
import { Assessment } from '@mui/icons-material';

const EvaluationsPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Evaluations
        </Typography>
        <Button variant="contained" startIcon={<Assessment />}>
          New Evaluation
        </Button>
      </Box>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            AI Investment Analysis
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This page will display AI-powered investment evaluations.
            Features coming in Phase 3:
          </Typography>
          <Box component="ul" sx={{ mt: 2 }}>
            <li>Multi-dimensional scoring dashboard</li>
            <li>Risk assessment visualization</li>
            <li>Financial analysis and projections</li>
            <li>Market opportunity analysis</li>
            <li>Team evaluation and recommendations</li>
            <li>Expert override capabilities</li>
            <li>Comparative analysis tools</li>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default EvaluationsPage;
