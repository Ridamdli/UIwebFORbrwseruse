import React, { useState, useEffect } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import { 
  AppBar, Box, Toolbar, Typography, Container, Button, 
  CssBaseline, ThemeProvider, createTheme, Alert, LinearProgress 
} from '@mui/material'
import HomeIcon from '@mui/icons-material/Home'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import SearchIcon from '@mui/icons-material/Search'
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary'
import SettingsIcon from '@mui/icons-material/Settings'

// Pages
import HomePage from './pages/Home'
import TaskRunnerPage from './pages/TaskRunner'
import ResearchPage from './pages/Research'
import RecordingsPage from './pages/Recordings'
import SettingsPage from './pages/Settings'

// API service
import api from './services/api'

// Theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
  },
})

function App() {
  const [apiAvailable, setApiAvailable] = useState<boolean | null>(null)
  const [apiCheckError, setApiCheckError] = useState<string | null>(null)

  useEffect(() => {
    // Check if the API is available when the app loads
    checkApiStatus()
    
    // Poll for API availability every 10 seconds
    const interval = setInterval(() => {
      checkApiStatus()
    }, 10000)
    
    return () => clearInterval(interval)
  }, [])
  
  const checkApiStatus = async () => {
    try {
      console.log('Checking API status...')
      const response = await api.healthCheck()
      
      if (response.status === 200) {
        console.log('API is available')
        setApiAvailable(true)
        setApiCheckError(null)
      } else {
        console.log('API responded but status is not OK')
        setApiAvailable(false)
        setApiCheckError('API server returned an unexpected response')
      }
    } catch (error: any) {
      console.error('API health check failed:', error)
      setApiAvailable(false)
      
      // Provide more detailed error information based on the error type
      if (error.code === 'ERR_NETWORK') {
        setApiCheckError('Cannot connect to API server. Server may be offline or not reachable.')
      } else if (error.response && error.response.status === 500) {
        setApiCheckError('API server encountered an internal error. Please check server logs.')
      } else {
        setApiCheckError(`API connection error: ${error.message}`)
      }
    }
  }

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static" color="primary">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Browser Use Web UI
            </Typography>
            <Button color="inherit" component={Link} to="/" startIcon={<HomeIcon />}>
              Home
            </Button>
            <Button color="inherit" component={Link} to="/task-runner" startIcon={<AutoFixHighIcon />}>
              Task Runner
            </Button>
            <Button color="inherit" component={Link} to="/research" startIcon={<SearchIcon />}>
              Research
            </Button>
            <Button color="inherit" component={Link} to="/recordings" startIcon={<VideoLibraryIcon />}>
              Recordings
            </Button>
            <Button color="inherit" component={Link} to="/settings" startIcon={<SettingsIcon />}>
              Settings
            </Button>
          </Toolbar>
        </AppBar>
        
        {apiAvailable === false && (
          <Alert severity="warning" variant="filled" sx={{ borderRadius: 0 }}>
            ⚠️ API server is not available. Please check your backend connection.
            {apiCheckError && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Error: {apiCheckError}
              </Typography>
            )}
            <Button 
              size="small" 
              variant="outlined" 
              color="inherit" 
              sx={{ ml: 2 }}
              onClick={checkApiStatus}
            >
              Retry Connection
            </Button>
          </Alert>
        )}
        
        {apiAvailable === null && (
          <LinearProgress sx={{ height: 4 }} />
        )}
        
        <Container component="main" sx={{ flexGrow: 1, py: 4 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/task-runner" element={<TaskRunnerPage />} />
            <Route path="/research" element={<ResearchPage />} />
            <Route path="/recordings" element={<RecordingsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </Container>
        
        <Box component="footer" sx={{ py: 2, bgcolor: 'background.paper', textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Browser Use Web UI © {new Date().getFullYear()}
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  )
}

export default App 