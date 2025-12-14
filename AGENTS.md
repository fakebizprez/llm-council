# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service, routing in `main.py`, council orchestration in `council.py`, OpenRouter client in `openrouter.py`, config in `config.py`.
- `frontend/`: React + Vite app, entry in `src/main.jsx`, UI in `src/App.jsx` and `src/components/`, styles in `src/App.css` and `src/index.css`.
- `data/`: Conversation JSON archives under `data/conversations/`; avoid committing sensitive runs.
- Root helpers: `start.sh` launches both services; `pyproject.toml` defines Python deps; `frontend/package.json` defines web scripts.

## Build, Test, and Development Commands
- Install backend deps: `uv sync`.
- Install frontend deps: `cd frontend && npm install`.
- Run full stack: `./start.sh` (backend on 8001, frontend on 5173).
- Manual dev: `uv run python -m backend.main` (API) and `cd frontend && npm run dev` (Vite server).
- Frontend checks: `cd frontend && npm run lint`. No formal backend lint script yet; keep code PEP 8-ish.

## Coding Style & Naming Conventions
- Python: 3.10+, prefer async HTTP via httpx, keep functions small; snake_case for vars/functions, CapWords for classes; drop unused imports; type hints where obvious.
- JavaScript/React: ES modules, 2-space indent, semicolons, single quotes; functional components + hooks; keep API calls in `src/api.js`; components live in `src/components/`.
- Linting: ESLint flat config with react-hooks/react-refresh; resolve warnings before sending changes.
- Filenames: `kebab-case` for assets, `PascalCase.jsx` for components, `snake_case.py` for modules.

## Testing Guidelines
- No automated suite yet. Prefer adding lightweight tests: Python (`pytest` under `backend/tests/`), JS (`vitest` or React Testing Library) if introduced.
- For now, sanity-check flows manually: start both services, create a conversation, send a prompt, verify stages 1-3 stream and conversations persist to `data/conversations/`.
- When adding tests, mirror fixtures to sample conversation JSON and keep test names descriptive (`test_handles_stage3_timeout`).

## Commit & Pull Request Guidelines
- Commits are short and imperative (e.g., `add vibe code warning`, `readme tweaks`). Keep scope focused.
- Include concise PR description: goal, key changes, and how to run/verify (`./start.sh` or dev servers + lint).
- Link related issues if any; add screenshots/GIFs for UI-facing tweaks.
- Avoid committing `.env` or generated conversation data; ensure secrets stay local.

## Configuration & Security
- Create `.env` in repo root with `OPENROUTER_API_KEY=...`; never commit it.
- Model selection lives in `backend/config.py` (`COUNCIL_MODELS`, `CHAIRMAN_MODEL`); adjust there and keep IDs valid for OpenRouter.
- Data now lives in SQLite (`data/conversations.db` by default). Override with `DB_PATH` env var if you want a different location or mount. Clear the DB if testing with sensitive prompts.
