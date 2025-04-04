import { Typography, Box, Paper, Grid, Card, CardContent, CardActions, Button } from '@mui/material';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome to Browser Use Web UI
      </Typography>
      
      <Typography variant="body1" paragraph>
        This platform allows you to control and automate web browsers using AI assistance.
        Choose one of the options below to get started.
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                Run Browser Tasks
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Execute browser tasks with AI assistance. 
                Control browser actions, navigate websites, and automate workflows.
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" component={Link} to="/tasks">Get Started</Button>
            </CardActions>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                Deep Research
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Perform in-depth research on any topic. The AI will search multiple 
                sources and compile comprehensive reports automatically.
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" component={Link} to="/research">Start Research</Button>
            </CardActions>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="div">
                View Recordings
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Browse and review recordings of previous browser sessions. 
                Useful for analysis and debugging of automated tasks.
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" component={Link} to="/recordings">View Recordings</Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>
      
      <Paper elevation={2} sx={{ p: 3, mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          About this Platform
        </Typography>
        <Typography variant="body2">
          Browser Use Web UI is a platform for AI-powered browser automation.
          It uses large language models to interpret natural language instructions
          and control web browsers to perform a wide variety of tasks.
        </Typography>
      </Paper>
    </Box>
  );
};

export default HomePage; 