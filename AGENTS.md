# AGENTS.md

## Project Overview
Codeless AI is a platform where users define interfaces and tests, and AI agents generate the implementation. It consists of a Python backend and a React/Vite frontend.

## Environment Setup

### Backend (Python)
- Install dependencies: `pip install -r requirements.txt`
- Environment variables should be set in `.env` (e.g., `OPENAI_API_KEY`).

### Frontend (Node.js)
- Navigate to frontend: `cd frontend`
- Install dependencies: `npm install`

## Running Tests
To run the backend test suite, use the following command from the root directory:
```bash
pytest --ignore=agents/test_generator.py --ignore=lib
```
Note: `agents/test_generator.py` and `lib` are explicitly ignored.

## Running the Application

### Web UI
- **Backend**: `python server.py` (starts on http://localhost:8000)
- **Frontend**: `cd frontend && npm run dev` (starts on http://localhost:5173)
- **Convenience Script**: `./start_app.sh` (starts both)

### CLI / Listener
To start the listener for a specific project:
```bash
python start.py <project-name>
```

## Directory Structure
- `agents/`: Contains the AI agent logic.
- `frontend/`: The React frontend application.
- `server.py`: The FastAPI/backend server entry point.
- `start.py`: The CLI entry point for the file listener.
- `demo.py`: A demo script.
