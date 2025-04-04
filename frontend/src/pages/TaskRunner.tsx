import React, { useState, useEffect } from 'react';
import { Typography, Box, Alert, CircularProgress, Grid } from '@mui/material';

import TaskForm from '../components/TaskForm';
import TaskViewer from '../components/TaskViewer';
import TaskHistory from '../components/TaskHistory';
import api from '../services/api';

// Mock data type for task history
interface TaskHistoryItem {
  task_id: string;
  status: string;
  task: string;
  created_at: string;
  recording_path: string | null;
}

const TaskRunnerPage: React.FC = () => {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [taskHistory, setTaskHistory] = useState<TaskHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // This would typically come from an API call to get task history
  // For now, we'll just use mock data that we'll update as we create tasks
  
  const handleTaskSubmit = (taskId: string) => {
    // Add the new task to the history
    const newTask: TaskHistoryItem = {
      task_id: taskId,
      status: 'running',
      task: 'New task', // This would come from the form input
      created_at: new Date().toISOString(),
      recording_path: null
    };
    
    setTaskHistory(prev => [newTask, ...prev]);
    
    // Set this as the active task
    setActiveTaskId(taskId);
  };
  
  const handleSelectTask = (taskId: string) => {
    setActiveTaskId(taskId);
  };
  
  const handleCloseTask = () => {
    setActiveTaskId(null);
  };
  
  // Update the task status when we receive updates
  const updateTaskStatus = (taskId: string, status: string, recordingPath: string | null = null) => {
    setTaskHistory(prev => 
      prev.map(task => 
        task.task_id === taskId 
          ? { ...task, status, recording_path: recordingPath || task.recording_path } 
          : task
      )
    );
  };
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Task Runner
      </Typography>
      
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
      
      {/* Task viewer (when a task is active) */}
      {activeTaskId && (
        <TaskViewer 
          taskId={activeTaskId}
          onClose={handleCloseTask}
        />
      )}
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          {/* Task form */}
          <TaskForm onTaskSubmit={handleTaskSubmit} />
        </Grid>
        
        <Grid item xs={12} md={6}>
          {/* Task history */}
          <TaskHistory
            tasks={taskHistory}
            onSelectTask={handleSelectTask}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default TaskRunnerPage; 