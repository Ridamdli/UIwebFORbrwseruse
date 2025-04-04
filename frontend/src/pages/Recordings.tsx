import React, { useState, useEffect } from 'react';
import { 
  Typography, Box, Alert, CircularProgress, Grid, 
  Card, CardContent, CardActions, Button, 
  CardMedia, Chip, Divider
} from '@mui/material';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import DeleteIcon from '@mui/icons-material/Delete';

import api from '../services/api';

interface Recording {
  filename: string;
  url: string;
  size: number;
  created_at: string;
}

const RecordingsPage: React.FC = () => {
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    fetchRecordings();
  }, []);
  
  const fetchRecordings = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.getRecordings();
      
      if (response.data && response.data.recordings) {
        setRecordings(response.data.recordings);
      } else {
        setRecordings([]);
      }
    } catch (err: any) {
      setError('Failed to fetch recordings. Please try again.');
      console.error('Error fetching recordings:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) {
      return bytes + ' B';
    } else if (bytes < 1024 * 1024) {
      return (bytes / 1024).toFixed(2) + ' KB';
    } else if (bytes < 1024 * 1024 * 1024) {
      return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    } else {
      return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
    }
  };
  
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Recordings
        </Typography>
        
        <Button 
          variant="outlined" 
          onClick={fetchRecordings}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>
      
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      {!loading && recordings.length === 0 && (
        <Alert severity="info">
          No recordings found. Run a task with recording enabled to create one.
        </Alert>
      )}
      
      <Grid container spacing={3}>
        {recordings.map((recording) => (
          <Grid item xs={12} sm={6} md={4} key={recording.filename}>
            <Card variant="outlined">
              <CardMedia
                component="div"
                sx={{
                  height: 160,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  bgcolor: 'background.paper',
                  color: 'text.secondary',
                }}
              >
                <VideoLibraryIcon sx={{ fontSize: 60 }} />
              </CardMedia>
              
              <CardContent>
                <Typography variant="h6" component="div" noWrap>
                  {recording.filename}
                </Typography>
                
                <Box sx={{ mt: 1, mb: 2 }}>
                  <Chip 
                    label={formatFileSize(recording.size)} 
                    size="small" 
                    sx={{ mr: 1 }} 
                  />
                  <Typography variant="caption" color="text.secondary">
                    {formatDate(recording.created_at)}
                  </Typography>
                </Box>
              </CardContent>
              
              <Divider />
              
              <CardActions>
                <Button 
                  size="small" 
                  href={recording.url}
                  target="_blank"
                  startIcon={<VideoLibraryIcon />}
                >
                  Play
                </Button>
                
                <Button 
                  size="small"
                  href={recording.url}
                  download={recording.filename}
                  startIcon={<CloudDownloadIcon />}
                >
                  Download
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default RecordingsPage; 