# Browser Use Web UI - Web Deployment

This is the web deployment version of the Browser Use Web UI, allowing the platform to be accessed online rather than just locally.

## Architecture

The project has been restructured for web deployment with the following architecture:

### Backend
- **FastAPI Server**: Provides REST API endpoints and WebSocket connections
- **Playwright Integration**: Browser automation through Playwright
- **Agent System**: AI agent architecture from the original project
- **Docker Support**: Containerized for easy deployment

### Frontend
- **React + TypeScript**: Modern web frontend with static typing
- **Material UI**: Component library for consistent UI
- **Axios**: HTTP client for API communication
- **WebSockets**: Real-time updates from browser tasks

## Prerequisites

- **Node.js 18+** - For frontend development
- **Python 3.11+** - For backend development
- **Docker & Docker Compose** - For containerized deployment

## Development Setup

### Backend

1. Set up a Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements-web.txt
   ```

3. Run the backend:
   ```bash
   cd backend
   python run.py
   ```

### Frontend

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Access the application at `http://localhost:5173`

## Deployment

### Docker Deployment

The simplest way to deploy is using Docker Compose:

```bash
docker-compose up -d
```

This will start both the backend and frontend in a containerized environment.

### Cloud Deployment Options

The application can be deployed to various cloud platforms:

#### Render

1. Create a web service for the backend
2. Connect to your GitHub repository
3. Set the root directory to `backend`
4. Set the build command: `pip install -r ../requirements-web.txt`
5. Set the start command: `cd backend && python run.py`

#### Railway

1. Create a new project
2. Connect to your GitHub repository
3. Add environment variables from `.env.example`
4. Railway will automatically detect the Dockerfile and deploy

## Environment Variables

See `.env.example` for required environment variables.

## API Documentation

Once running, API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Roadmap

1. **Authentication**: User login/registration with Supabase
2. **Multi-user Support**: Multiple users with isolated workspaces
3. **Usage History**: Track and review past tasks
4. **Custom Agents**: User-defined agent templates
5. **Enhanced UI**: Improved UI/UX for specific use cases

## License

See the [LICENSE](LICENSE) file for licensing information. 