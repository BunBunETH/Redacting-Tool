import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  Message as MessageIcon,
  Security as SecurityIcon,
  TrendingUp as TrendingUpIcon,
  Timer as TimerIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsResponse, activityResponse] = await Promise.all([
          api.get('/mock/vault/stats'),
          api.get('/mock/vault/mock')
        ]);
        setStats(statsResponse.data);
        setRecentActivity(activityResponse.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const StatCard = ({ title, value, icon, color, subtitle }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{ color, mr: 1 }}>{icon}</Box>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div" sx={{ mb: 1 }}>
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  const getConfidenceColor = (score) => {
    if (score >= 0.98) return 'success';
    if (score >= 0.90) return 'primary';
    return 'warning';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffHours < 1) {
      const diffMinutes = Math.floor((now - date) / (1000 * 60));
      return `${diffMinutes} minutes ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hours ago`;
    } else {
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
  };

  if (loading) {
    return (
      <Layout>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h4" gutterBottom>
            Dashboard
          </Typography>
        </Grid>
        
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Messages"
            value={stats?.total_entries.toLocaleString()}
            icon={<MessageIcon fontSize="large" />}
            color="primary.main"
            subtitle="Messages processed"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Redacted Items"
            value={stats?.total_redactions.toLocaleString()}
            icon={<SecurityIcon fontSize="large" />}
            color="error.main"
            subtitle="Sensitive data items found"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Accuracy Rate"
            value={`${Math.round((stats?.feedback_ratio || 0) * 100)}%`}
            icon={<TrendingUpIcon fontSize="large" />}
            color="success.main"
            subtitle={`${stats?.positive_feedback} correct out of ${stats?.total_redactions} reviews`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Processing Time"
            value={stats?.avg_processing_time}
            icon={<TimerIcon fontSize="large" />}
            color="info.main"
            subtitle="Average processing time per message"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Protection Score"
            value="A+"
            icon={<ShieldIcon fontSize="large" />}
            color="secondary.main"
            subtitle="Data protection rating"
          />
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Message ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>User</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="center">Redactions</TableCell>
                    <TableCell align="center">Confidence</TableCell>
                    <TableCell>Processing</TableCell>
                    <TableCell>Time</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentActivity.map((activity) => (
                    <TableRow key={activity.id} hover>
                      <TableCell>
                        <Tooltip title={`Conversation: ${activity.conversation_id}`}>
                          <span>{activity.message_id}</span>
                        </Tooltip>
                      </TableCell>
                      <TableCell>{activity.message_type}</TableCell>
                      <TableCell>{activity.user_id}</TableCell>
                      <TableCell>
                        <Chip 
                          label={activity.is_archived ? 'Archived' : 'Active'}
                          color={activity.is_archived ? 'default' : 'success'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={activity.redaction_count}
                          color={activity.redaction_count > 3 ? 'error' : 'primary'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title={`${(activity.confidence_score * 100).toFixed(1)}%`}>
                          <Chip
                            label={`${Math.round(activity.confidence_score * 100)}%`}
                            color={getConfidenceColor(activity.confidence_score)}
                            size="small"
                          />
                        </Tooltip>
                      </TableCell>
                      <TableCell>{activity.processing_time}s</TableCell>
                      <TableCell>
                        <Tooltip title={new Date(activity.created_at).toLocaleString()}>
                          <span>{formatDate(activity.created_at)}</span>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Layout>
  );
};

export default Dashboard; 