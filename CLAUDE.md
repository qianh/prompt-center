# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Prompt Center is a comprehensive prompt management application for organizing, versioning, comparing, and testing prompts across multiple LLM providers. The application consists of a FastAPI backend with PostgreSQL database and a React TypeScript frontend with TailwindCSS.

## Common Development Commands

### Backend (Python with uv)

```bash
# Setup and activate virtual environment
cd backend
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run single test file
pytest tests/contract/test_prompts.py

# Database migrations
alembic upgrade head                    # Apply migrations
alembic revision --autogenerate -m "Description"  # Create new migration

# Code formatting and linting
black src tests                         # Format code
isort src tests                         # Sort imports
ruff check src tests                    # Lint code
mypy src                                # Type checking
```

### Frontend (React with Vite)

```bash
# Setup
cd frontend
npm install

# Run development server (starts on http://localhost:3000)
npm run dev

# Build for production
npm run build

# Run type checking (linting)
npm run lint

# Run tests
npm test
npm run test:ui                         # Run with UI
npm run test:coverage                   # Run with coverage report

# Preview production build
npm run preview
```

### Docker Development

```bash
# Start all services (frontend, backend, database)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build
```

## Architecture

### Backend Structure

The backend follows a layered architecture pattern:

- **`src/api/v1/`**: API route definitions and endpoints
- **`src/models/`**: SQLAlchemy ORM models representing database tables
- **`src/schemas/`**: Pydantic schemas for request/response validation
- **`src/crud/`**: Database operation functions (Create, Read, Update, Delete)
- **`src/services/`**: Business logic layer including LLM provider integrations
- **`src/core/`**: Core utilities (config, database, logging)
- **`alembic/versions/`**: Database migration files

Key models:
- **Prompt**: Base prompt entity with title, description, tags
- **PromptVersion**: Versioned content for prompts with parent-child relationships
- **Comparison**: Stores comparison test results (A/B testing, cross-LLM testing)
- **LLMConfig**: Stores LLM provider configurations with encrypted API keys

### Frontend Structure

The frontend is a React SPA with component-based architecture:

- **`src/components/prompts/`**: Prompt management components
- **`src/components/versions/`**: Version control components
- **`src/components/comparisons/`**: Comparison testing interface
- **`src/components/ui/`**: Reusable UI components (shadcn/ui based)

The frontend uses:
- React Query (`@tanstack/react-query`) for server state management
- React Router for navigation
- React Hook Form with Zod for form validation
- Axios for HTTP requests
- TailwindCSS + shadcn/ui for styling

### LLM Integration

The `src/services/llm.py` module provides a unified interface for multiple LLM providers:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude models)
- Google AI (Gemini models)

All LLM calls are async with proper error handling and rate limiting.

### Database

PostgreSQL database with:
- Full-text search capabilities for prompts
- Version control with parent-child relationships
- Encrypted storage for LLM API keys (via ENCRYPTION_KEY env var)

## Configuration

### Environment Variables

Create `.env` in the project root:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/prompt_center
ENCRYPTION_KEY=<generate with: openssl rand -hex 32>
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=...
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
```

## Testing Approach

### Backend Tests
- Contract tests in `backend/tests/contract/` verify API endpoints match specification contracts in `specs/001-prompt-management/contracts/`
- Tests use pytest with async support (`pytest-asyncio`)
- FastAPI TestClient for endpoint testing

### Frontend Tests
- Component tests using Vitest
- Testing library for React components

## Specification-Driven Development

The project uses a specification-first approach:
- Feature specifications in `specs/001-prompt-management/spec.md`
- API contracts defined as JSON schemas in `specs/001-prompt-management/contracts/`
- Contract tests validate implementation matches specifications

## Key Design Patterns

### Version Control System
Prompts use an immutable version system:
- Each edit creates a new PromptVersion
- Versions maintain parent-child relationships via `parent_version_id`
- Allows branching, comparison, and rollback

### Comparison Engine
Two types of comparisons:
1. **Version Comparison**: Multiple versions of same prompt on one LLM
2. **Cross-LLM Comparison**: One prompt version across multiple LLMs

Results stored as snapshots in the Comparison table with full context.

### Service Layer Pattern
Business logic separated into service modules:
- `services/prompt_version.py`: Version management logic
- `services/comparison.py`: Comparison execution and result processing
- `services/llm.py`: LLM provider abstraction

This keeps API routes thin and enables easier testing and reuse.

## Code Style

### Backend (Python)
- Black formatter (line length: 88)
- isort for import sorting
- Type hints required (enforced by mypy)
- Ruff for linting
- Target: Python 3.11+

### Frontend (TypeScript)
- ESLint with React plugins
- Prettier for formatting
- TypeScript strict mode
- Target: Modern browsers with ES2020+

## API Documentation

When backend is running, interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
