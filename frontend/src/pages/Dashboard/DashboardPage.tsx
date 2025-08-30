import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  Assessment,
  Business,
  Description,
  Add,
  Schedule,
  CheckCircle,
  Warning,
} from '@mui/icons-material';

import { useAuthStore } from '../../store/authStore';

const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();

  // Mock data for demonstration
  const stats = [
    {
      title: 'Total Ventures',
      value: '24',
      change: '+12%',
      icon: <Business />,
      color: 'primary',
    },
    {
      title: 'Evaluations',
      value: '18',
      change: '+8%',
      icon: <Assessment />,
      color: 'success',
    },
    {
      title: 'Documents',
      value: '156',
      change: '+24%',
      icon: <Description />,
      color: 'info',
    },
    {
      title: 'Avg. Score',
      value: '7.2',
      change: '+0.3',
      icon: <TrendingUp />,
      color: 'warning',
    },
  ];

  const recentActivity = [
    {
      id: 1,
      type: 'evaluation',
      title: 'TechStart AI completed evaluation',
      time: '2 hours ago',
      status: 'completed',
      icon: <CheckCircle color="success" />,
    },
    {
      id: 2,
      type: 'document',
      title: 'New pitch deck uploaded for FinanceFlow',
      time: '4 hours ago',
      status: 'processing',
      icon: <Schedule color="warning" />,
    },
    {
      id: 3,
      type: 'venture',
      title: 'HealthTech Solutions added to portfolio',
      time: '1 day ago',
      status: 'new',
      icon: <Business color="primary" />,
    },
    {
      id: 4,
      type: 'alert',
      title: 'Review required for GreenEnergy evaluation',
      time: '2 days ago',
      status: 'attention',
      icon: <Warning color="error" />,
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'new':
        return 'info';
      case 'attention':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome back, {user?.firstName}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what's happening with your investment evaluations today.
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 1,
                      backgroundColor: `${stat.color}.light`,
                      color: `${stat.color}.contrastText`,
                      mr: 2,
                    }}
                  >
                    {stat.icon}
                  </Box>
                  <Box>
                    <Typography variant="h4" component="div">
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.title}
                    </Typography>
                  </Box>
                </Box>
                <Typography
                  variant="body2"
                  color="success.main"
                  sx={{ fontWeight: 'medium' }}
                >
                  {stat.change} from last month
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  Add New Venture
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Description />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  Upload Documents
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Assessment />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  Start Evaluation
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List>
                {recentActivity.map((activity) => (
                  <ListItem key={activity.id} divider>
                    <ListItemIcon>{activity.icon}</ListItemIcon>
                    <ListItemText
                      primary={activity.title}
                      secondary={activity.time}
                    />
                    <Chip
                      label={activity.status}
                      size="small"
                      color={getStatusColor(activity.status) as any}
                      variant="outlined"
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
