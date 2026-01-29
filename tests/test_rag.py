import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio  # <--- THIS FIXES THE ASYNC ERROR
async def test_rag_update_concurrency(client):
    mock_reviews = [MagicMock(page_content="Review 1")]
    mock_profs = [MagicMock(page_content="Prof Smith")]

    with patch("backend.src.api.rag.get_school_reviews", return_value=mock_reviews), \
            patch("backend.src.api.rag.get_school_professors", return_value=mock_profs), \
            patch("backend.src.api.rag.VectorManager") as MockVM:
        vm_instance = MockVM.return_value

        response = client.post("/rag/update")

        assert response.status_code == 200
        assert "Successfully updated" in response.json()["message"]

        assert vm_instance.ingest_data.call_count == 2
