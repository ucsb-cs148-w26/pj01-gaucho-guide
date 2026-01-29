from unittest.mock import MagicMock, patch
from backend.src.managers.session_manager import SessionManager
from backend.src.managers.vector_manager import VectorManager


# --- SESSION MANAGER TESTS ---
def test_session_crud(mock_db_connection):
    """Test creating, saving, and loading messages in SQLite."""
    manager = SessionManager()  # Will use the mocked :memory: connection

    session_id = manager.create_session(name="Test Chat")
    assert session_id is not None

    manager.save_message(session_id, "human", "Hello")
    manager.save_message(session_id, "ai", "Hi there")

    history = manager.load_history(session_id)
    assert len(history) == 2
    assert history[0].content == "Hello"
    assert history[1].content == "Hi there"


# --- VECTOR MANAGER TESTS ---
def test_vector_manager_routing():
    """Test that the route_query method selects the correct namespace."""

    # We mock the internal components of VectorManager
    with patch("backend.src.managers.vector_manager.Pinecone"), \
            patch("backend.src.managers.vector_manager.OllamaEmbeddings"), \
            patch("backend.src.managers.vector_manager.ChatOllama") as MockOllama:
        # Setup the mock LLM for routing
        mock_llm = MockOllama.return_value

        # Create a dummy object to mimic the Pydantic model output
        class MockRoute:
            namespace = "professor_data"

        mock_llm.with_structured_output.return_value.invoke.return_value = MockRoute()

        vm = VectorManager(api_key="fake-key")

        # Test routing
        namespace = vm.route_query("Who is Professor Smith?")
        assert namespace == "professor_data"


def test_vector_manager_search_fallback():
    with patch("backend.src.managers.vector_manager.Pinecone"), \
            patch("backend.src.managers.vector_manager.OllamaEmbeddings"), \
            patch("backend.src.managers.vector_manager.ChatOllama") as MockOllama:
        vm = VectorManager(api_key="fake-key")
        vm.route_query = MagicMock(return_value="professor_data")

        vm.vector_store = MagicMock()
        vm.vector_store.similarity_search.side_effect = [
            Exception("Namespace error"),
            ["Fallback Doc"]
        ]

        results = vm.std_search("query")

        assert results == ["Fallback Doc"]