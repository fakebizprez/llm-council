# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service.
  - `main.py`: API routes (including streaming) and app entry point.
  - `council.py`: Orchestration of the 3-stage LLM council process.
  - `openrouter.py`: Client for OpenRouter API.
  - `storage.py`: SQLite database operations (`data/conversations.db`).
  - `config.py`: Configuration and model constants.
- `frontend/`: React + Vite app.
  - `src/main.jsx`: Entry point.
  - `src/App.jsx`: Main application component.
  - `src/api.js`: API client for backend communication.
  - `src/components/`: UI components (ChatInterface, Stages, Sidebar).
  - `src/App.css`, `src/index.css`: Styles.
- `data/`: Created at runtime. Contains `conversations.db` (SQLite) for storing chat history.
- Root helpers:
  - `start.sh`: Launches both backend and frontend services.
  - `pyproject.toml`: Python dependencies (managed by `uv`).
  - `frontend/package.json`: Node dependencies and scripts.

## Build, Test, and Development Commands
- **Backend Setup**: `uv sync` to install dependencies.
- **Frontend Setup**: `cd frontend && npm install`.
- **Run Full Stack**: `./start.sh` (Backend: http://localhost:8001, Frontend: http://localhost:5173).
- **Manual Development**:
  - Backend: `uv run python -m backend.main`
  - Frontend: `cd frontend && npm run dev`
- **Linting**:
  - Frontend: `cd frontend && npm run lint`
  - Backend: Follow PEP 8.

## Coding Style & Naming Conventions
- **Python**: Python 3.10+. Async `httpx` for requests. Snake_case for variables/functions, PascalCase for classes. Type hints encouraged.
- **JavaScript/React**: ES modules. Functional components with hooks. 2-space indentation. PascalCase for components (`.jsx`), kebab-case for assets.
- **State Management**: React hooks for local state.
- **API**: Keep backend routes in `backend/main.py` and frontend calls in `frontend/src/api.js`.

## Testing Guidelines
- Currently, no automated test suite exists.
- **Manual Verification**:
  1. Start services (`./start.sh`).
  2. Create a new conversation.
  3. Send a prompt (e.g., "Why is the sky blue?").
  4. Verify all 3 stages (Collection, Ranking, Synthesis) stream correctly.
  5. Refresh page to verify history persistence from SQLite.
- Future tests: Place Python tests in `backend/tests/` (using `pytest`).

## Commit & Pull Request Guidelines
- **Commits**: Imperative mood (e.g., "Add stage 4", "Fix streaming bug").
- **PRs**: Description should include what changed and how to verify.
- **Secrets**: NEVER commit `.env` or `data/conversations.db`.

## Configuration & Security
- **Environment**: Create `.env` in root with `OPENROUTER_API_KEY=...`.
- **Models**: Configured in `backend/config.py` (`COUNCIL_MODELS`, `CHAIRMAN_MODEL`).
- **Database**: defaults to `data/conversations.db`. Can be overridden with `DB_PATH`.
