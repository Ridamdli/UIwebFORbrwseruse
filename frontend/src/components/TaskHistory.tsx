import React, { useState } from 'react';
import { 
  Box, Typography, Paper, List, ListItem, ListItemText, 
  Chip, IconButton, Divider, Tooltip
} from '@mui/material';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import ErrorIcon from '@mui/icons-material/Error';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';

interface TaskHistoryProps {
  tasks: Array<{
    task_id: string;
    status: string;
    task: string;
    created_at: string;
    recording_path: string | null;
  }>;
  onSelectTask: (taskId: string) => void;
}

const TaskHistory: React.FC<TaskHistoryProps> = ({ tasks, onSelectTask }) => {
  // Function to get status color
  const getStatusChip = (status: string) => {
    switch (status) {
      case 'completed':
        return <Chip 
          icon={<CheckCircleIcon />} 
          label="Completed" 
          size="small" 
          color="success" 
        />;
      case 'failed':
        return <Chip 
          icon={<ErrorIcon />} 
          label="Failed" 
          size="small" 
          color="error" 
        />;
      case 'running':
        return <Chip 
          icon={<HourglassEmptyIcon />} 
          label="Running" 
          size="small" 
          color="primary" 
        />;
      default:
        return <Chip 
          icon={<HourglassEmptyIcon />} 
          label={status} 
          size="small" 
        />;
    }
  };
  
  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  return (
    <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        Recent Tasks
      </Typography>
      
      {tasks.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
          No task history available.
        </Typography>
      ) : (
        <List disablePadding>
          {tasks.map((task, index) => (
            <React.Fragment key={task.task_id}>
              {index > 0 && <Divider />}
              <ListItem
                sx={{
                  px: 2,
                  py: 1.5,
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
                secondaryAction={
                  <Box>
                    <Tooltip title="View task details">
                      <IconButton
                        edge="end"
                        aria-label="view"
                        onClick={() => onSelectTask(task.task_id)}
                      >
                        <PlayCircleOutlineIcon />
                      </IconButton>
                    </Tooltip>
                    
                    {task.recording_path && (
                      <Tooltip title="View recording">
                        <IconButton
                          edge="end"
                          aria-label="recording"
                          href={`/recordings/${task.recording_path.split('/').pop()}`}
                          target="_blank"
                        >
                          <VideoLibraryIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                }
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography
                        variant="body1"
                        sx={{
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          maxWidth: '300px',
                        }}
                      >
                        {task.task || `Task ${task.task_id.substring(0, 8)}...`}
                      </Typography>
                      {getStatusChip(task.status)}
                    </Box>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {formatDate(task.created_at)}
                    </Typography>
                  }
                />
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default TaskHistory; 