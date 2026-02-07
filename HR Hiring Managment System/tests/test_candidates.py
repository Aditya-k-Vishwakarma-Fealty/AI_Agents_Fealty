import pytest
from unittest.mock import patch, MagicMock
from fastapi import UploadFile

@pytest.mark.asyncio
async def test_submit_candidate(client):
    """Test candidate submission."""
    # Mock dependencies using module-level patches for ResumeParsingAgent internals
    with patch("app.services.candidate_service.save_resume_file") as mock_save, \
         patch("app.services.candidate_service.extract_text_from_resume") as mock_extract, \
         patch("app.agents.resume_agent.ResumeParsingAgent.parse_resume") as mock_parse_resume, \
         patch("app.services.candidate_service.chroma_client") as mock_chroma:
        
        # Setup mocks
        mock_save.return_value = "/tmp/dummy_resume.pdf"
        mock_extract.return_value = "Content"
        mock_parse_resume.return_value = {
            "status": "success",
            "data": {
                "name": "John Doe",
                "email": "john@example.com",
                "skills": ["Python", "FastAPI"]
            }
        }
        
        # Verify embedding call metadata uses string for list
        mock_chroma.add_resume_embedding.side_effect = lambda **kwargs: "mock_resume_doc_id"

        # Prepare form data
        files = {"resume": ("resume.pdf", b"dummy content", "application/pdf")}
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        }

        response = await client.post("/candidates/submit", data=data, files=files)
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "candidate_id" in result
        
        # Check that add_resume_embedding was called and skills were stringified
        assert mock_chroma.add_resume_embedding.called
        call_args = mock_chroma.add_resume_embedding.call_args
        assert call_args.kwargs["metadata"]["skills"] == "Python, FastAPI"
        
        # Verify candidate is in DB
        candidate_id = result["candidate_id"]
        get_response = await client.get(f"/candidates/{candidate_id}")
        assert get_response.status_code == 200
        candidate_data = get_response.json()
        assert candidate_data["name"] == "John Doe"
        assert candidate_data["email"] == "john@example.com"

@pytest.mark.asyncio
async def test_evaluate_candidate(client):
    """Test candidate evaluation."""
    # 1. Create a role (need mocking for role creation as well)
    role_id = 0
    with patch("app.api.roles.chroma_client") as mock_role_chroma:
        mock_role_chroma.add_role_embedding.return_value = "mock_role_doc_id"
        role_data = {
            "title": "Python Developer",
            "description": "Python dev needed",
            "required_skills": ["Python"],
            "experience_required": 2
        }
        role_resp = await client.post("/roles/create", json=role_data)
        role_id = role_resp.json()["role_id"]

    # 2. Submit a candidate
    candidate_id = 0
    with patch("app.services.candidate_service.save_resume_file") as mock_save, \
         patch("app.services.candidate_service.extract_text_from_resume") as mock_extract, \
         patch("app.agents.resume_agent.ResumeParsingAgent.parse_resume") as mock_parse_resume, \
         patch("app.services.candidate_service.chroma_client") as mock_chroma:
        
        mock_save.return_value = "/tmp/dummy_resume.pdf"
        mock_extract.return_value = "Content"
        mock_parse_resume.return_value = {
            "status": "success",
            "data": {"name": "Jane Doe", "skills": ["Python"]}
        }
        mock_chroma.add_resume_embedding.return_value = "mock_resume_doc_id"

        files = {"resume": ("resume.pdf", b"content", "application/pdf")}
        data = {"name": "Jane Doe", "email": "jane@example.com"}
        cand_resp = await client.post("/candidates/submit", data=data, files=files)
        candidate_id = cand_resp.json()["candidate_id"]

    # 3. Evaluate candidate
    with patch("app.agents.resume_agent.ResumeParsingAgent.parse_resume") as mock_parse_resume, \
         patch("app.services.candidate_service.chroma_client") as mock_chroma, \
         patch("app.services.candidate_service.scoring_agent") as mock_scoring, \
         patch("app.services.candidate_service.shortlist_agent") as mock_shortlist:
        
        # Mocks for evaluation
        mock_parse_resume.return_value = {
            "status": "success",
            "data": {"name": "Jane Doe", "skills": ["Python"]}
        }
        mock_chroma.get_similarity_score.return_value = 0.85
        mock_scoring.score_candidate.return_value = {
            "status": "success",
            "data": {
                "resume_score": 85,
                "match_percentage": 85,
                "strengths": ["Python"],
                "gaps": [],
                "ai_reasoning": "Good match"
            }
        }
        # Note: shortlist_agent.evaluate_candidate return schema wasn't fully checked, assuming dict
        mock_shortlist.evaluate_candidate.return_value = {
            "status": "shortlisted",
            "reason": "High score"
        }

        eval_req = {"role_id": role_id}
        response = await client.post(f"/candidates/{candidate_id}/evaluate", json=eval_req)
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["score_data"]["resume_score"] == 85
