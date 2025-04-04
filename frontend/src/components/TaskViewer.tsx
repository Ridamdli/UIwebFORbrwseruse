import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, Typography, Paper, Grid, LinearProgress, 
  Button, Card, CardContent, Alert, Divider,
  Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import StopIcon from '@mui/icons-material/Stop';
import ReplayIcon from '@mui/icons-material/Replay';

import api from '../services/api';
import websocketService from '../services/websocket';

interface TaskViewerProps {
  taskId: string;
  onClose: () => void;
}

interface TaskStatus {
  status: string;
  progress: number;
  screenshot: string | null;
  model_actions: string | null;
  model_thoughts: string | null;
  final_result: string | null;
  errors: string | null;
  recording_path: string | null;
}

/**
 * Ensure the screenshot data is in the correct format with data URI scheme
 */
const formatScreenshotData = (screenshotData: string | null): string | null => {
  if (!screenshotData) return null;
  
  // If already has data URI scheme prefix, return as is
  if (screenshotData.startsWith('data:image')) {
    return screenshotData;
  }
  
  // If it's just a base64 string without the prefix, add it
  return `data:image/jpeg;base64,${screenshotData}`;
};

const TaskViewer: React.FC<TaskViewerProps> = ({ taskId, onClose }) => {
  const [status, setStatus] = useState<TaskStatus>({
    status: 'starting',
    progress: 0,
    screenshot: null,
    model_actions: null,
    model_thoughts: null,
    final_result: null,
    errors: null,
    recording_path: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [screenshotError, setScreenshotError] = useState<string | null>(null);
  
  // Create a memoized function to handle WebSocket updates
  const handleStatusUpdate = useCallback((data: any) => {
    console.log('Received status update:', data);
    setStatus(prevStatus => ({
      ...prevStatus,
      ...data
    }));
    
    // Reset screenshot error when new screenshot is received
    if (data.screenshot) {
      setScreenshotError(null);
    }
  }, []);

  // Function to fetch the latest status from the API
  const fetchStatus = useCallback(async () => {
    try {
      console.log(`Fetching status for task ${taskId}`);
      const response = await api.getAgentStatus(taskId);
      if (response.data) {
        console.log('Received task status:', response.data);
        setStatus(prevStatus => ({
          ...prevStatus,
          ...response.data
        }));
        
        // Reset screenshot error when new status is fetched
        if (response.data.screenshot) {
          setScreenshotError(null);
        }
      }
    } catch (err: any) {
      setError('Failed to fetch task status');
      console.error('Error fetching task status:', err);
    } finally {
      setLoading(false);
    }
  }, [taskId]);
  
  // Function to connect to WebSocket with retry logic
  const connectWebSocket = useCallback(async () => {
    if (reconnectAttempts > 3) {
      console.log('Max reconnect attempts reached, falling back to polling');
      setError('Could not establish real-time connection. Falling back to periodic updates.');
      
      // Fall back to polling every 3 seconds
      const pollInterval = setInterval(() => {
        fetchStatus();
      }, 3000);
      
      return () => clearInterval(pollInterval);
    }
    
    try {
      console.log(`Connecting to WebSocket for task ${taskId}, attempt ${reconnectAttempts + 1}`);
      
      // Disconnect any existing connection first
      if (websocketService.isConnected()) {
        websocketService.disconnect();
      }
      
      await websocketService.connect(taskId);
      console.log('WebSocket connected successfully');
      setIsConnected(true);
      setError(null);
      
      // Register message handlers
      console.log('Registering update message handler');
      const unsubscribe = websocketService.onMessage('update', handleStatusUpdate);
      
      // Register connection handlers
      const onConnectionClosed = () => {
        console.log('WebSocket connection closed');
        setIsConnected(false);
        setReconnectAttempts(prev => prev + 1);
      };
      
      const unsubscribeClose = websocketService.onClose(onConnectionClosed);
      const unsubscribeError = websocketService.onError(onConnectionClosed);
      
      return () => {
        console.log('Cleaning up WebSocket handlers');
        unsubscribe();
        unsubscribeClose();
        unsubscribeError();
        websocketService.disconnect();
      };
    } catch (err) {
      console.error('WebSocket connection error:', err);
      setError('Failed to connect to real-time updates');
      setIsConnected(false);
      setReconnectAttempts(prev => prev + 1);
      
      // Try to reconnect after a delay
      const reconnectTimeout = setTimeout(() => {
        connectWebSocket();
      }, 3000);
      
      return () => clearTimeout(reconnectTimeout);
    }
  }, [taskId, reconnectAttempts, handleStatusUpdate, fetchStatus]);
  
  // Main effect for fetching status and setting up WebSocket
  useEffect(() => {
    console.log(`TaskViewer initialized for task ${taskId}`);
    
    // Initial status fetch
    fetchStatus();
    
    // Set up WebSocket connection
    const cleanup = connectWebSocket();
    
    // Cleanup function
    return () => {
      console.log('TaskViewer unmounting, cleaning up resources');
      if (typeof cleanup === 'function') {
        cleanup();
      } else if (cleanup instanceof Promise) {
        cleanup.then(fn => {
          if (typeof fn === 'function') {
            fn();
          }
        });
      }
      
      // Ensure WebSocket is disconnected
      if (websocketService.isConnected()) {
        websocketService.disconnect();
      }
    };
  }, [taskId, connectWebSocket, fetchStatus]);
  
  // Function to manually reconnect WebSocket
  const handleReconnect = () => {
    setReconnectAttempts(0);
    connectWebSocket();
  };
  
  const stopTask = async () => {
    try {
      await api.stopAgent(taskId);
      // The status will be updated via the WebSocket
      fetchStatus(); // Also fetch immediately to ensure we get the updated status
    } catch (err) {
      setError('Failed to stop the task');
      console.error('Error stopping task:', err);
    }
  };
  
  // Handle screenshot load error
  const handleScreenshotError = () => {
    console.error('Error loading screenshot');
    setScreenshotError('Failed to load screenshot. The image may be corrupted or in an unsupported format.');
  };
  
  // Format model thoughts with line breaks
  const formattedThoughts = status.model_thoughts ? 
    status.model_thoughts.split('\\n').map((line, i) => (
      <React.Fragment key={i}>
        {line}
        <br />
      </React.Fragment>
    )) : null;
  
  const formattedActions = status.model_actions ? 
    status.model_actions.split('\\n').map((line, i) => (
      <React.Fragment key={i}>
        {line}
        <br />
      </React.Fragment>
    )) : null;
  
  // Format final results with line breaks
  const formattedResults = status.final_result ? 
    status.final_result.split('\\n').map((line, i) => (
      <React.Fragment key={i}>
        {line}
        <br />
      </React.Fragment>
    )) : null;
    
  // Format the screenshot URL
  const screenshotUrl = formatScreenshotData(status.screenshot);
  
  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Task {taskId.substring(0, 8)}... {status.status === 'completed' ? '✅' : status.status === 'failed' ? '❌' : '🔄'}
          </Typography>
          
          <Box>
            {['running', 'starting'].includes(status.status) && (
              <Button 
                variant="contained" 
                color="error" 
                startIcon={<StopIcon />}
                onClick={stopTask}
                sx={{ mr: 1 }}
              >
                Stop
              </Button>
            )}
            
            <Button 
              variant="outlined"
              onClick={onClose}
            >
              Close
            </Button>
          </Box>
        </Box>
        
        {!isConnected && status.status !== 'completed' && status.status !== 'failed' && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Not connected to real-time updates. Some information may be outdated.
            <Button 
              size="small" 
              startIcon={<ReplayIcon />}
              onClick={handleReconnect}
              sx={{ ml: 2 }}
            >
              Reconnect
            </Button>
          </Alert>
        )}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Status: {status.status.charAt(0).toUpperCase() + status.status.slice(1)}
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={status.progress * 100} 
            sx={{ height: 10, borderRadius: 5 }}
          />
        </Box>
        
        <Grid container spacing={3}>
          {/* Screenshot Section */}
          <Grid item xs={12} md={7}>
            <Typography variant="subtitle1" gutterBottom>
              Browser View
            </Typography>
            <Box 
              sx={{ 
                border: '1px solid #ccc', 
                borderRadius: 1, 
                height: 500, 
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                bgcolor: 'background.paper',
                overflow: 'hidden',
                position: 'relative'
              }}
            >
              {screenshotUrl ? (
                <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
                  <img 
                    src={screenshotUrl} 
                    alt="Browser screenshot" 
                    style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', margin: 'auto', display: 'block' }}
                    onError={handleScreenshotError}
                  />
                  {screenshotError && (
                    <Alert severity="error" sx={{ position: 'absolute', bottom: 0, left: 0, right: 0 }}>
                      {screenshotError}
                    </Alert>
                  )}
                </Box>
              ) : (
                <Typography color="text.secondary">
                  Waiting for screenshot...
                </Typography>
              )}
            </Box>
          </Grid>
          
          {/* Agent Activity Section */}
          <Grid item xs={12} md={5}>
            <Typography variant="subtitle1" gutterBottom>
              Agent Activity
            </Typography>
            
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>Agent Thoughts</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box 
                  sx={{ 
                    p: 2, 
                    maxHeight: 200, 
                    overflowY: 'auto',
                    bgcolor: 'background.paper',
                    borderRadius: 1,
                    fontSize: '0.875rem',
                    fontFamily: 'monospace'
                  }}
                >
                  {formattedThoughts || 'No thoughts recorded yet.'}
                </Box>
              </AccordionDetails>
            </Accordion>
            
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>Agent Actions</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box 
                  sx={{ 
                    p: 2, 
                    maxHeight: 200, 
                    overflowY: 'auto',
                    bgcolor: 'background.paper',
                    borderRadius: 1,
                    fontSize: '0.875rem',
                    fontFamily: 'monospace'
                  }}
                >
                  {formattedActions || 'No actions recorded yet.'}
                </Box>
              </AccordionDetails>
            </Accordion>
          </Grid>
          
          {/* Results Section (appears when task is complete) */}
          {['completed', 'failed'].includes(status.status) && (
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" gutterBottom>
                Final Results
              </Typography>
              
              {status.errors && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {status.errors}
                </Alert>
              )}
              
              {status.final_result && (
                <Card variant="outlined" sx={{ mt: 2 }}>
                  <CardContent>
                    <Typography variant="body1" component="div">
                      {formattedResults}
                    </Typography>
                  </CardContent>
                </Card>
              )}
              
              {status.recording_path && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Recording
                  </Typography>
                  <Button 
                    variant="outlined" 
                    href={`/recordings/${status.recording_path.split('/').pop()}`}
                    target="_blank"
                  >
                    View Recording
                  </Button>
                </Box>
              )}
            </Grid>
          )}
        </Grid>
      </Paper>
    </Box>
  );
};

export default TaskViewer; 