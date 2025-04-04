# Browser-Use Web UI

A powerful web interface for browser automation using AI agents with real-time visualization.

## Description

Browser-Use Web UI provides an intuitive interface for controlling and monitoring AI-powered browser automation. This application allows users to create automation tasks using natural language prompts, observe the automation in real time through screenshot updates, and retrieve results once tasks are completed.

## Key Features

- **Natural Language Task Creation**: Define browser automation tasks using simple text prompts
- **Real-time Visualization**: Watch the browser automation execute with live screenshot updates
- **Task Management**: Create, monitor, and stop tasks from a unified interface
- **Task History**: View past automation runs and their results
- **Responsive Design**: Works across desktop and mobile devices

## Technologies Used

### Frontend
- React
- TypeScript
- Material UI
- Vite
- Axios for API communication
- WebSocket for real-time updates

### Backend
- Python
- FastAPI
- Uvicorn
- Websockets
- Pillow for image processing
- Optional: Browser-Use package for real browser automation

## Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.9+
- pip
- npm or yarn

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/browser-use-web-ui.git
   cd browser-use-web-ui
   ```

2. Create and activate a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```bash
   python simple_api.py
   ```

   The backend server will be available at http://127.0.0.1:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn
   ```

3. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

   The frontend will be available at http://localhost:5173

## Environment Variables

### Backend
Create a `.env` file in the `backend` directory with these variables:

```
# Server Configuration
PORT=8000
HOST=127.0.0.1

# Browser Configuration
HEADLESS_MODE=false

# Optional: Browser-Use Configuration 
BROWSER_USE_API_KEY=your_api_key_if_needed
```

### Frontend
Create a `.env` file in the `frontend` directory with these variables:

```
# API Configuration
VITE_API_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000
```

## Deployment

### Frontend Deployment to Vercel

1. Set up the following environment variables in Vercel:
   - `VITE_API_URL`: URL of your deployed backend API
   - `VITE_WS_URL`: WebSocket URL of your deployed backend

2. Configure the build settings:
   - Build Command: `npm run build` or `yarn build`
   - Output Directory: `dist`
   - Install Command: `npm install` or `yarn install`

### Backend Deployment

The backend can be deployed to any service that supports Python applications:

1. Install production dependencies:
   ```bash
   pip install -r requirements.txt gunicorn
   ```

2. Start the server:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker simple_api:app
   ```

## API Documentation

When the backend is running, access the API documentation at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## License

This project is licensed under the MIT License - see the LICENSE file for details.
