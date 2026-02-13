import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.src.main import app


@pytest.fixture
def mock_db_connection():
    """Forces SessionManager to use an in-memory database."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    with patch("backend.src.managers.session_manager.sqlite3.connect", return_value=conn):
        yield conn
    conn.close()


@pytest.fixture
def mock_llm():
    """Mocks ChatOllama in the correct location."""
    target_path = "backend.src.api.chat.ChatOllama"

    with patch(target_path) as MockOllama:
        instance = MockOllama.return_value

        async def async_response(*args, **kwargs):
            return MagicMock(content="[MOCK] You should go to Freebirds!")

        instance.ainvoke.side_effect = async_response

        yield instance


@pytest.fixture
def mock_vector_manager():
    """Mocks VectorManager so Pinecone is not needed."""
    target_path = "backend.src.api.chat.VectorManager"

    with patch(target_path) as MockVM:
        instance = MockVM.return_value
        mock_doc = MagicMock()
        mock_doc.page_content = "Review: The rec cen has a great pool."

        instance.std_search.return_value = [mock_doc]

        yield instance


@pytest.fixture
def client():
    return TestClient(app)
