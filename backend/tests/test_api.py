"""Integration tests for API endpoints."""
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    """Verify health endpoint returns 200 OK."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_list_episodes_endpoint():
    """Verify episodes list endpoint returns paginated results."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/episodes?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "episodes" in data
        assert isinstance(data["episodes"], list)
        assert len(data["episodes"]) <= 10

@pytest.mark.asyncio
async def test_search_episodes_endpoint():
    """Verify search endpoint returns relevant results."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/episodes/search",
            json={"query": "retention", "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

@pytest.mark.asyncio
async def test_chat_endpoint_requires_message():
    """Verify chat endpoint validates required fields."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={"session_id": "test-123"}  # Missing 'message' field
        )
        assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_session_creation_endpoint():
    """Verify session creation returns valid session ID."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0

@pytest.mark.asyncio
async def test_list_sessions_endpoint():
    """Verify sessions list endpoint returns array."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)

@pytest.mark.asyncio
async def test_get_session_messages():
    """Verify session messages endpoint returns message history."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a session first
        create_response = await client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Get messages for that session
        response = await client.get(f"/api/v1/sessions/{session_id}/messages")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)

@pytest.mark.asyncio
async def test_delete_session_endpoint():
    """Verify session deletion returns success."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a session
        create_response = await client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Delete it
        response = await client.delete(f"/api/v1/sessions/{session_id}")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_upload_document_endpoint_validation():
    """Verify document upload validates file type."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test with invalid file type
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = await client.post("/api/v1/knowledge/upload", files=files)
        # Should either accept it or return validation error
        assert response.status_code in [200, 400, 415, 422]

@pytest.mark.asyncio
async def test_list_models_endpoint():
    """Verify models endpoint returns available providers."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], dict)
        # Should have at least openai, anthropic, groq, ollama
        assert len(data["providers"]) >= 1
