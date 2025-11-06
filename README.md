# Prompt Center

A comprehensive prompt management application that enables users to organize, version, compare, and test prompts across multiple LLM providers with an intuitive modern interface.

## Features

- **Prompt Repository**: Store, search, and organize prompts with tags and metadata
- **Version Control**: Create and manage multiple versions of prompts with change tracking
- **A/B Testing**: Compare different prompt versions on the same LLM
- **Cross-LLM Testing**: Test the same prompt across different LLM providers
- **Snapshot Storage**: Save and organize comparison results over time
- **Multi-LLM Support**: Configure and use OpenAI, Anthropic, Google AI, and more
- **Modern UI**: Beautiful, responsive interface built with React and TailwindCSS

## Tech Stack

### Frontend
- React 18 with TypeScript
- TailwindCSS + shadcn/ui components
- Vite for build tooling
- React Query for data fetching

### Backend
- Python 3.11+ with FastAPI
- SQLAlchemy with Alembic migrations
- PostgreSQL database
- Pydantic for data validation

### LLM Integration
- OpenAI SDK
- Anthropic SDK
- Google AI SDK
- Async execution with proper error handling

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ with uv (for local backend development)

### Using Docker (Recommended)

1. Clone the repository
2. Copy environment files:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
3. Start the application:
   ```bash
   docker-compose up -d
   ```
4. Access the application at http://localhost:3000
5. API documentation at http://localhost:8000/docs

### Local Development

#### Backend

```bash
cd backend
uv sync
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
alembic upgrade head
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/prompt_center

# Encryption key for API keys (generate with: openssl rand -hex 32)
ENCRYPTION_KEY=your-encryption-key-here

# LLM Provider API Keys (optional - can be configured in UI)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_AI_API_KEY=your-google-ai-key

# Application
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
```

### LLM Provider Setup

1. Navigate to the application
2. Go to Settings → LLM Providers
3. Add your provider configurations:
   - **OpenAI**: API key, model (gpt-4, gpt-3.5-turbo)
   - **Anthropic**: API key, model (claude-3-sonnet, claude-3-haiku)
   - **Google AI**: API key, model (gemini-pro)

## Usage

### Creating Prompts

1. Click "New Prompt" in the sidebar
2. Enter title, description, and content
3. Add relevant tags
4. Save to create the first version

### Managing Versions

1. Select a prompt from the list
2. Click "Create Version" to make a copy
3. Edit the content and add change notes
4. Save as new version or update current

### Running Comparisons

#### Version Comparison
1. Select multiple versions of the same prompt
2. Choose an LLM provider
3. Enter test input
4. Click "Compare Versions"

#### Cross-LLM Comparison
1. Select a single prompt version
2. Choose multiple LLM providers
3. Enter test input
4. Click "Compare Across LLMs"

### Viewing Snapshots

1. Go to "Comparisons" in the sidebar
2. Browse saved comparison results
3. Filter by type, date, or prompts used
4. Export results in various formats

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Code Style

- Backend: Black, isort, mypy
- Frontend: ESLint, Prettier
- Pre-commit hooks ensure consistent formatting

## Architecture

The application follows a clean architecture pattern:

- **Frontend**: React SPA with component-based architecture
- **Backend**: FastAPI with service layer pattern
- **Database**: PostgreSQL with full-text search capabilities
- **LLM Integration**: Unified interface with provider-specific adapters

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the API documentation
- Review the user guide in the application
