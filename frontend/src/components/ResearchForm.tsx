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

const ResearchForm: React.FC<{
  onResearchSubmit: (taskId: string) => void;
}> = ({ onResearchSubmit }) => {
  const [researchTask, setResearchTask] = useState('');
  const [llmProvider, setLlmProvider] = useState('openai');
  const [llmModel, setLlmModel] = useState('gpt-4-turbo');
  const [useVision, setUseVision] = useState(true);
  const [headless, setHeadless] = useState(false);
  const [maxSearchIterations, setMaxSearchIterations] = useState(3);
  const [maxQueriesPerIteration, setMaxQueriesPerIteration] = useState(2);
  
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
    if (!researchTask.trim()) {
      setError('Research task description is required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.startResearch({
        research_task: researchTask,
        max_search_iteration: maxSearchIterations,
        max_query_per_iter: maxQueriesPerIteration,
        llm_provider: llmProvider,
        llm_model_name: llmModel,
        llm_temperature: 0.7,
        use_vision: useVision,
        headless: headless,
        use_own_browser: false,
      });
      
      const taskId = response.data.task_id;
      onResearchSubmit(taskId);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start the research. Please try again.');
      console.error('Error starting research:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        Create a New Research Task
      </Typography>
      
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              id="researchTask"
              label="Research Task"
              multiline
              rows={3}
              fullWidth
              value={researchTask}
              onChange={(e) => setResearchTask(e.target.value)}
              required
              placeholder="Describe what you want to research"
              helperText="What topic do you want to research? Be specific about your requirements."
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
          
          <Grid item xs={12} md={6}>
            <TextField
              id="max-search-iterations"
              label="Max Search Iterations"
              type="number"
              fullWidth
              value={maxSearchIterations}
              onChange={(e) => setMaxSearchIterations(parseInt(e.target.value))}
              InputProps={{ inputProps: { min: 1, max: 10 } }}
              helperText="Number of search iterations to perform"
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              id="max-queries-per-iteration"
              label="Max Queries per Iteration"
              type="number"
              fullWidth
              value={maxQueriesPerIteration}
              onChange={(e) => setMaxQueriesPerIteration(parseInt(e.target.value))}
              InputProps={{ inputProps: { min: 1, max: 5 } }}
              helperText="Number of search queries per iteration"
            />
          </Grid>
          
          <Grid item xs={12}>
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
              {loading ? <CircularProgress size={24} /> : 'Start Research'}
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default ResearchForm; 