import uuid


def test_chat_response_success(client, mock_llm, mock_vector_manager, mock_db_connection):
    session_id = str(uuid.uuid4())
    payload = {
        "chat_history": [{"type": "human", "content": "Does UCSB have a gym?"}],
        "chat_session_id": session_id,
        "model_name": "llama3"
    }

    response = client.post("/chat/response", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "[MOCK] You should go to Freebirds!"

    # Verify DB save happened
    cursor = mock_db_connection.cursor()
    cursor.execute("SELECT content FROM messages WHERE session_id=?", (session_id,))
    rows = cursor.fetchall()
    assert len(rows) >= 2
    mock_vector_manager.std_search.assert_called_once()


def test_chat_internal_error_handling(client, mock_vector_manager, mock_llm):
    """Verifies graceful handling if VectorManager fails."""
    # Simulate a Pinecone crash
    mock_vector_manager.std_search.side_effect = Exception("Pinecone down")

    session_id = str(uuid.uuid4())
    payload = {
        "chat_history": [{"type": "human", "content": "Hello"}],
        "chat_session_id": session_id,
        "model_name": "llama3"
    }

    response = client.post("/chat/response", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "response" in data
    assert "trouble accessing my brain" in data["response"]
