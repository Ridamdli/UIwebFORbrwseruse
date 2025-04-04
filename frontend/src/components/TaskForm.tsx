import React, { useState } from 'react';
import { 
  Box, Button, TextField, FormControl, InputLabel, 
  Select, MenuItem, FormControlLabel, Switch, 
  Typography, Paper, Grid, CircularProgress, Alert
} from '@mui/material';

import api from '../services/api';

interface LLMOption {
  provider: string;
  models: string[];
}

const llmOptions: LLMOption[] = [
  {
    provider: 'openai',
    models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
  },
  {
    provider: 'anthropic',
    models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
  },
  {
    provider: 'google',
    models: ['gemini-pro', 'gemini-ultra']
  },
  {
    provider: 'ollama',
    models: ['llama3', 'mistral', 'mixtral']
  }
];

const TaskForm: React.FC<{
  onTaskSubmit: (taskId: string) => void;
}> = ({ onTaskSubmit }) => {
  const [task, setTask] = useState('');
  const [additionalInfo, setAdditionalInfo] = useState('');
  const [llmProvider, setLlmProvider] = useState('openai');
  const [llmModel, setLlmModel] = useState('gpt-4-turbo');
  const [useVision, setUseVision] = useState(true);
  const [enableRecording, setEnableRecording] = useState(true);
  const [headless, setHeadless] = useState(false);
  const [maxSteps, setMaxSteps] = useState(50);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Get the models for the selected provider
  const availableModels = llmOptions.find(option => option.provider === llmProvider)?.models || [];

  const handleProviderChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    const provider = event.target.value as string;
    setLlmProvider(provider);
    // Reset the model to the first available model for this provider
    const models = llmOptions.find(option => option.provider === provider)?.models || [];
    if (models.length > 0) {
      setLlmModel(models[0]);
    }
  };
  
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    // Validate required fields
    if (!task.trim()) {
      setError('Task description is required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.runAgent({
        prompt: task,
        options: {
          llm_provider: llmProvider,
          llm_model_name: llmModel,
          llm_temperature: 0.7,
          use_vision: useVision,
          additional_info: additionalInfo,
          enable_recording: enableRecording,
          headless: headless,
          max_steps: maxSteps
        }
      });
      
      const taskId = response.data.task_id;
      onTaskSubmit(taskId);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start the task. Please try again.');
      console.error('Error starting task:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        Create a New Browser Task
      </Typography>
      
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              id="task"
              label="Task Description"
              multiline
              rows={3}
              fullWidth
              value={task}
              onChange={(e) => setTask(e.target.value)}
              required
              placeholder="Describe what you want the browser to do"
              helperText="Be specific about what you want the agent to accomplish"
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              id="additionalInfo"
              label="Additional Information (Optional)"
              multiline
              rows={2}
              fullWidth
              value={additionalInfo}
              onChange={(e) => setAdditionalInfo(e.target.value)}
              placeholder="Provide any additional context or constraints for the task"
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="llm-provider-label">LLM Provider</InputLabel>
              <Select
                labelId="llm-provider-label"
                id="llm-provider"
                value={llmProvider}
                label="LLM Provider"
                onChange={(e) => handleProviderChange(e as any)}
              >
                {llmOptions.map((option) => (
                  <MenuItem key={option.provider} value={option.provider}>
                    {option.provider.charAt(0).toUpperCase() + option.provider.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="llm-model-label">LLM Model</InputLabel>
              <Select
                labelId="llm-model-label"
                id="llm-model"
                value={llmModel}
                label="LLM Model"
                onChange={(e) => setLlmModel(e.target.value as string)}
              >
                {availableModels.map((model) => (
                  <MenuItem key={model} value={model}>
                    {model}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              id="max-steps"
              label="Maximum Steps"
              type="number"
              fullWidth
              value={maxSteps}
              onChange={(e) => setMaxSteps(parseInt(e.target.value))}
              InputProps={{ inputProps: { min: 1, max: 200 } }}
              helperText="Maximum number of steps the agent will take"
            />
          </Grid>
          
          <Grid item xs={12} md={8}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
              <FormControlLabel
                control={
                  <Switch 
                    checked={useVision} 
                    onChange={(e) => setUseVision(e.target.checked)} 
                  />
                }
                label="Use Vision"
              />
              
              <FormControlLabel
                control={
                  <Switch 
                    checked={enableRecording} 
                    onChange={(e) => setEnableRecording(e.target.checked)} 
                  />
                }
                label="Record Session"
              />
              
              <FormControlLabel
                control={
                  <Switch 
                    checked={headless} 
                    onChange={(e) => setHeadless(e.target.checked)} 
                  />
                }
                label="Headless Mode"
              />
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              fullWidth
              disabled={loading}
              sx={{ mt: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Start Task'}
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default TaskForm; 