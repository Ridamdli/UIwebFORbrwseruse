import React, { useState } from 'react';
import { Typography, Box, Grid } from '@mui/material';

import ResearchForm from '../components/ResearchForm';
import TaskViewer from '../components/TaskViewer';

const ResearchPage: React.FC = () => {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  
  const handleResearchSubmit = (taskId: string) => {
    setActiveTaskId(taskId);
  };
  
  const handleCloseTask = () => {
    setActiveTaskId(null);
  };
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Deep Research
      </Typography>
      
      {/* Research viewer (when a task is active) */}
      {activeTaskId && (
        <TaskViewer 
          taskId={activeTaskId}
          onClose={handleCloseTask}
        />
      )}
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={8} sx={{ mx: 'auto' }}>
          {/* Research form */}
          <ResearchForm onResearchSubmit={handleResearchSubmit} />
          
          {/* Information about the research feature */}
          {!activeTaskId && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom>
                About Deep Research
              </Typography>
              <Typography variant="body1" paragraph>
                Deep Research uses an AI agent to conduct comprehensive research on any topic.
                The agent will perform multiple search iterations and compile the results into a well-structured report.
              </Typography>
              <Typography variant="body1" paragraph>
                This feature is ideal for:
              </Typography>
              <ul>
                <li>
                  <Typography variant="body1">Market research and competitive analysis</Typography>
                </li>
                <li>
                  <Typography variant="body1">Academic literature reviews</Typography>
                </li>
                <li>
                  <Typography variant="body1">Technology trend analysis</Typography>
                </li>
                <li>
                  <Typography variant="body1">Fact-checking and information gathering</Typography>
                </li>
              </ul>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Note: The research process can take several minutes depending on the complexity of the topic.
                You'll be able to see live updates as the agent works.
              </Typography>
            </Box>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResearchPage; 