import axios from 'axios';

// Create API instance
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Define API methods
export default {
  // Task management
  runAgent: (data: any) => api.post('/agent/run', data),
  getAgentStatus: (taskId: string) => api.get(`/agent/status/${taskId}`),
  stopAgent: (taskId: string) => api.post(`/agent/stop/${taskId}`),
  
  // Health check
  healthCheck: () => api.get('/'),
}; 