import React, { useState, useEffect, useCallback } from 'react';
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
  Alert,
  Divider,
  Chip,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Archive as ArchiveIcon,
  Feedback as FeedbackIcon,
  VisibilityOff as VisibilityOffIcon,
  Compare as CompareIcon,
  Undo as UndoIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { 
  getVaultEntries, 
  archiveVaultEntry, 
  addVaultFeedback,
  revertRedaction 
} from '../services/api';
import { useSnackbar } from 'notistack';

const Vault = () => {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [feedbackDialog, setFeedbackDialog] = useState(false);
  const [showOriginal, setShowOriginal] = useState(false);
  const [viewMode, setViewMode] = useState('single'); // 'single' or 'compare'
  const [feedback, setFeedback] = useState({
    is_positive: true,
    feedback_notes: '',
  });
  const [revertDialog, setRevertDialog] = useState(false);
  const { enqueueSnackbar } = useSnackbar();

  const handleCloseDialog = () => {
    setFeedbackDialog(false);
    setShowOriginal(false);
    setViewMode('single');
    setSelectedEntry(null);
    setFeedback({
      is_positive: true,
      feedback_notes: '',
    });
  };

  const fetchEntries = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getVaultEntries(page);
      setEntries(response.data);
      setTotalPages(Math.ceil(response.data.length / 10));
    } catch (error) {
      console.error('Error fetching vault entries:', error);
      enqueueSnackbar('Failed to fetch vault entries', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  }, [page, enqueueSnackbar]);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  const handleFeedbackSubmit = async () => {
    try {
      await addVaultFeedback(selectedEntry.id, {
        ...feedback,
        reviewed_by: 'current_user',
      });
      enqueueSnackbar('Feedback submitted successfully', { variant: 'success' });
      handleCloseDialog();
      fetchEntries();
    } catch (error) {
      console.error('Error submitting feedback:', error);
      enqueueSnackbar('Failed to submit feedback', { variant: 'error' });
    }
  };

  const handleArchive = async (entryId) => {
    try {
      await archiveVaultEntry(entryId);
      enqueueSnackbar('Entry archived successfully', { variant: 'success' });
      fetchEntries();
    } catch (error) {
      console.error('Error archiving entry:', error);
      enqueueSnackbar('Failed to archive entry', { variant: 'error' });
    }
  };

  const handleToggleViewMode = () => {
    setViewMode(viewMode === 'single' ? 'compare' : 'single');
  };

  const handleRevertClick = () => {
    setRevertDialog(true);
  };

  const handleRevertConfirm = async () => {
    try {
      setLoading(true);
      await revertRedaction(selectedEntry.id);
      enqueueSnackbar('Redaction reverted successfully. Original message restored in Intercom.', { 
        variant: 'success',
        autoHideDuration: 4000
      });
      setRevertDialog(false);
      handleCloseDialog();
      fetchEntries(); // Refresh the list
    } catch (error) {
      console.error('Error reverting redaction:', error);
      enqueueSnackbar('Failed to revert redaction. Please try again.', { 
        variant: 'error',
        autoHideDuration: 4000
      });
    } finally {
      setLoading(false);
    }
  };

  const renderMessageContent = () => {
    if (!selectedEntry) return null;

    if (viewMode === 'compare') {
      return (
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Paper 
              sx={{ 
                p: 2, 
                backgroundColor: '#f5f5f5',
                height: '100%',
                position: 'relative'
              }}
            >
              <Typography variant="subtitle2" gutterBottom color="text.secondary">
                Redacted Version
              </Typography>
              <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-wrap' }}>
                {selectedEntry.redacted_message}
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={6}>
            <Paper 
              sx={{ 
                p: 2, 
                backgroundColor: '#fff3e0',
                height: '100%',
                position: 'relative'
              }}
            >
              <Typography variant="subtitle2" gutterBottom color="text.secondary">
                Original Version
              </Typography>
              <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-wrap' }}>
                {selectedEntry.original_message}
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      );
    }

    return (
      <Paper 
        sx={{ 
          p: 2, 
          backgroundColor: showOriginal ? '#fff3e0' : '#f5f5f5',
          position: 'relative' 
        }}
      >
        <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-wrap' }}>
          {showOriginal ? selectedEntry.original_message : selectedEntry.redacted_message}
        </Typography>
        <IconButton
          onClick={() => setShowOriginal(!showOriginal)}
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
          }}
        >
          {showOriginal ? <VisibilityOffIcon /> : <VisibilityIcon />}
        </IconButton>
      </Paper>
    );
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
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              {selectedEntry ? 'Review Redaction' : 'View Details'}
            </Typography>
            <Box>
              <Tooltip title="Toggle View Mode">
                <IconButton onClick={handleToggleViewMode} sx={{ mr: 1 }}>
                  <CompareIcon />
                </IconButton>
              </Tooltip>
              {viewMode === 'single' && (
                <Tooltip title={showOriginal ? "Show Redacted" : "Show Original"}>
                  <IconButton onClick={() => setShowOriginal(!showOriginal)}>
                    {showOriginal ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedEntry && (
            <>
              <Box sx={{ mb: 2, mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Message Content:
                  </Typography>
                  <Box>
                    <Chip 
                      label={selectedEntry.message_type} 
                      color="primary" 
                      size="small" 
                      sx={{ mr: 1 }}
                    />
                    <Tooltip title="Revert Redaction in Intercom">
                      <IconButton
                        onClick={handleRevertClick}
                        color="warning"
                        sx={{ mr: 1 }}
                      >
                        <UndoIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
                {renderMessageContent()}
                {(showOriginal || viewMode === 'compare') && (
                  <Alert severity="warning" sx={{ mt: 1 }}>
                    You are viewing sensitive information. Handle with care.
                  </Alert>
                )}
              </Box>
              <Box sx={{ mb: 2 }}>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Revert Redaction
                  </Typography>
                  <Typography variant="body2">
                    If this redaction is incorrect, click the undo button above to revert it. 
                    This will restore the original message in Intercom and mark this entry as a false positive.
                  </Typography>
                </Alert>
              </Box>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Redaction Details:
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Confidence Score
                      </Typography>
                      <Typography variant="h6">
                        {(selectedEntry.confidence_score * 100).toFixed(1)}%
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Redactions Found
                      </Typography>
                      <Typography variant="h6">
                        {selectedEntry.redaction_count}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
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
                label={feedback.is_positive ? "Redaction is correct" : "Redaction needs improvement"}
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
                placeholder="Provide specific feedback about the redaction..."
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={handleCloseDialog}
          >
            Cancel
          </Button>
          <Button onClick={handleFeedbackSubmit} variant="contained" color="primary">
            Submit Feedback
          </Button>
        </DialogActions>
      </Dialog>

      {/* Revert Confirmation Dialog */}
      <Dialog
        open={revertDialog}
        onClose={() => setRevertDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Confirm Revert Redaction
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Warning: This action cannot be undone
            </Typography>
            <Typography variant="body2">
              This will restore the original message in Intercom and mark this entry as a false positive.
              Are you sure you want to proceed?
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRevertDialog(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleRevertConfirm} 
            variant="contained" 
            color="warning"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Confirm Revert'}
          </Button>
        </DialogActions>
      </Dialog>
    </Layout>
  );
};

export default Vault; 