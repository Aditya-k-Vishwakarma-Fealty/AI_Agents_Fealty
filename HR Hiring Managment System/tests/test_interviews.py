import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

@pytest.mark.asyncio
async def test_schedule_interview(client):
    """Test scheduling an interview."""
    # 1. Create Role and Candidate
    role_id = 0
    candidate_id = 0
    
    # Mock chroma for role creation
    with patch("app.api.roles.chroma_client") as mock_role_chroma:
        mock_role_chroma.add_role_embedding.return_value = "mock_role_doc_id"
        role_resp = await client.post("/roles/create", json={
            "title": "Backend Dev",
            "description": "Desc",
            "required_skills": ["Python"],
            "experience_required": 3
        })
        role_id = role_resp.json()["role_id"]

    # Mock dependencies for candidate submission
    with patch("app.services.candidate_service.save_resume_file") as mock_save, \
         patch("app.services.candidate_service.extract_text_from_resume") as mock_extract, \
         patch("app.agents.resume_agent.ResumeParsingAgent.parse_resume") as mock_parse_resume, \
         patch("app.services.candidate_service.chroma_client") as mock_chroma:
         
        mock_save.return_value = "/tmp/dummy.pdf"
        mock_extract.return_value = "Content"
        mock_parse_resume.return_value = {
            "status": "success", "data": {"name": "Test User", "email": "test@example.com"}
        }
        mock_chroma.add_resume_embedding.return_value = "mock_resume_id"
        
        files = {"resume": ("resume.pdf", b"content", "application/pdf")}
        data = {"name": "Test User", "email": "test@example.com"}
        cand_resp = await client.post("/candidates/submit", data=data, files=files)
        candidate_id = cand_resp.json()["candidate_id"]

    # 2. Test Schedule
    # Since EmailTool is imported inside the function, we patch the class where it is defined
    with patch("app.tools.email_tool.EmailTool") as MockEmailTool:
        mock_instance = MockEmailTool.return_value
        mock_instance.send_interview_invite.return_value = {"status": "success"}
        
        payload = {
            "candidate_id": candidate_id,
            "role_id": role_id,
            "interview_datetime": "2023-12-25T10:00:00"
        }
        
        response = await client.post("/interviews/schedule", json=payload)
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_instance.send_interview_invite.assert_called_once()

@pytest.mark.asyncio
async def test_submit_interview(client):
    """Test submitting interview feedback."""
    # Need Candidate and Role IDs.
    # We will mock EvaluationService.
    # Use patch("app.api.interviews.EvaluationService") with AsyncMock return value for async methods
    
    with patch("app.api.interviews.EvaluationService") as MockService:
        mock_service_instance = MockService.return_value
        # evaluate_interview is awaited in the API, so it must be an AsyncMock
        mock_service_instance.evaluate_interview = AsyncMock(return_value={
            "status": "success",
            "interview_id": 123,
            "ai_evaluation": "Good"
        })
        
        payload = {
            "candidate_id": 1,
            "role_id": 1,
            "interviewer_name": "Interviewer",
            "communication_score": 8.0,
            "knowledge_score": 9.0,
            "confidence_score": 7.5,
            "feedback": "Good candidate"
        }
        
        response = await client.post("/interviews/submit", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
