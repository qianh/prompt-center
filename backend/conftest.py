"""
Pytest configuration and fixtures for the Prompt Center API.
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app

# Test database URL (in-memory SQLite for contract tests)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # This will be implemented in Task 1.2
    # For now, return None since we're in contract testing phase
    return None


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client."""
    # Database dependency override will be added in Task 1.2
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_prompt_data():
    """Sample prompt data for testing."""
    return {
        "title": "Test Prompt",
        "description": "A test prompt for contract testing",
        "content": "This is a test prompt content",
        "tags": ["test", "sample"],
        "change_notes": "Initial version"
    }


@pytest.fixture
def sample_version_data():
    """Sample version data for testing."""
    return {
        "content": "Updated prompt content",
        "change_notes": "Updated version"
    }


@pytest.fixture
def sample_comparison_data():
    """Sample comparison data for testing."""
    return {
        "name": "Test Comparison",
        "description": "A test comparison",
        "type": "version_comparison",
        "input_text": "Test input for comparison",
        "prompt_version_ids": ["version-1", "version-2"],
        "save_snapshot": True
    }
