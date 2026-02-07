import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_create_role(client):
    """Test creating a new role."""
    role_data = {
        "title": "Senior Software Engineer",
        "description": "We are looking for a Senior Software Engineer with Python experience.",
        "required_skills": ["Python", "FastAPI", "SQL"],
        "experience_required": 5
    }

    # Mock chroma_client to avoid actual vector DB calls
    with patch("app.api.roles.chroma_client") as mock_chroma:
        mock_chroma.add_role_embedding.return_value = "mock_doc_id"
        
        response = await client.post("/roles/create", json=role_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["role"]["title"] == role_data["title"]
        assert data["role"]["jd_embedding_id"] == "mock_doc_id"
        
        # Verify embedding call metadata uses string for list
        mock_chroma.add_role_embedding.assert_called_once()
        call_args = mock_chroma.add_role_embedding.call_args
        assert call_args.kwargs["metadata"]["required_skills"] == "Python, FastAPI, SQL"

@pytest.mark.asyncio
async def test_get_roles(client):
    """Test listing roles."""
    # Create a role first
    role_data = {
        "title": "Junior Developer",
        "description": "Junior dev needed.",
        "required_skills": ["Python"],
        "experience_required": 1
    }
    
    with patch("app.api.roles.chroma_client") as mock_chroma:
        mock_chroma.add_role_embedding.return_value = "mock_doc_id_2"
        await client.post("/roles/create", json=role_data)

    response = await client.get("/roles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["title"] == role_data["title"]

@pytest.mark.asyncio
async def test_get_role_by_id(client):
    """Test getting a role by ID."""
    role_data = {
        "title": "Product Manager",
        "description": "PM needed.",
        "required_skills": ["Agile"],
        "experience_required": 3
    }
    
    with patch("app.api.roles.chroma_client") as mock_chroma:
        mock_chroma.add_role_embedding.return_value = "mock_doc_id_3"
        create_response = await client.post("/roles/create", json=role_data)
        role_id = create_response.json()["role_id"]

    response = await client.get(f"/roles/{role_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == role_data["title"]
    assert data["id"] == role_id
