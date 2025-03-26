import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Pagination,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Archive as ArchiveIcon,
  Feedback as FeedbackIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import axios from 'axios';

const Vault = () => {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [feedbackDialog, setFeedbackDialog] = useState(false);
  const [feedback, setFeedback] = useState({
    is_positive: true,
    feedback_notes: '',
  });

  const fetchEntries = async () => {
    try {
      const response = await axios.get(`/api/v1/vault/entries?page=${page}&page_size=10`);
      setEntries(response.data.items);
      setTotalPages(Math.ceil(response.data.total / 10));
    } catch (error) {
      console.error('Error fetching vault entries:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, [page]);

  const handleFeedbackSubmit = async () => {
    try {
      await axios.post(`/api/v1/vault/entries/${selectedEntry.id}/feedback`, {
        ...feedback,
        reviewed_by: 'current_user', // This should come from auth context
      });
      setFeedbackDialog(false);
      fetchEntries();
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const handleArchive = async (entryId) => {
    try {
      await axios.post(`/api/v1/vault/entries/${entryId}/archive`);
      fetchEntries();
    } catch (error) {
      console.error('Error archiving entry:', error);
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
            Vault
          </Typography>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Message ID</TableCell>
                    <TableCell>Conversation ID</TableCell>
                    <TableCell>User ID</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {entries.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell>{entry.message_id}</TableCell>
                      <TableCell>{entry.conversation_id}</TableCell>
                      <TableCell>{entry.user_id}</TableCell>
                      <TableCell>
                        {entry.is_archived ? 'Archived' : 'Active'}
                      </TableCell>
                      <TableCell>
                        {new Date(entry.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View Details">
                          <IconButton
                            onClick={() => {
                              setSelectedEntry(entry);
                              setFeedbackDialog(true);
                            }}
                          >
                            <VisibilityIcon />
                          </IconButton>
                        </Tooltip>
                        {!entry.is_archived && (
                          <>
                            <Tooltip title="Archive">
                              <IconButton
                                onClick={() => handleArchive(entry.id)}
                              >
                                <ArchiveIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Provide Feedback">
                              <IconButton
                                onClick={() => {
                                  setSelectedEntry(entry);
                                  setFeedbackDialog(true);
                                }}
                              >
                                <FeedbackIcon />
                              </IconButton>
                            </Tooltip>
                          </>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(e, value) => setPage(value)}
                color="primary"
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Feedback Dialog */}
      <Dialog
        open={feedbackDialog}
        onClose={() => setFeedbackDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {selectedEntry ? 'Provide Feedback' : 'View Details'}
        </DialogTitle>
        <DialogContent>
          {selectedEntry && (
            <>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1">Original Message:</Typography>
                <Typography variant="body1">{selectedEntry.original_message}</Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1">Redacted Message:</Typography>
                <Typography variant="body1">{selectedEntry.redacted_message}</Typography>
              </Box>
              <FormControlLabel
                control={
                  <Switch
                    checked={feedback.is_positive}
                    onChange={(e) =>
                      setFeedback({ ...feedback, is_positive: e.target.checked })
                    }
                  />
                }
                label="Positive Feedback"
              />
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Feedback Notes"
                value={feedback.feedback_notes}
                onChange={(e) =>
                  setFeedback({ ...feedback, feedback_notes: e.target.value })
                }
                sx={{ mt: 2 }}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackDialog(false)}>Cancel</Button>
          <Button onClick={handleFeedbackSubmit} variant="contained">
            Submit Feedback
          </Button>
        </DialogActions>
      </Dialog>
    </Layout>
  );
};

export default Vault; 