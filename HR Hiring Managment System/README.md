# AI-Powered HR Hiring Management System

A production-ready, AI-powered HR hiring management system that automates the entire hiring lifecycle from candidate intake to final selection using FastAPI, LangChain agents, MySQL, and ChromaDB.

## 🎯 Features

- **Automated Resume Parsing**: AI-powered extraction of structured data from PDF/DOCX resumes
- **Intelligent Candidate Scoring**: Semantic matching against job descriptions with explainable AI reasoning
- **Automated Shortlisting**: Threshold-based candidate filtering with batch processing
- **Email Automation**: Gmail API integration for shortlist/rejection/interview invitations
- **Interview Evaluation**: AI-assisted assessment of interview performance
- **Final Ranking**: Weighted scoring combining resume and interview evaluations
- **RESTful API**: Complete FastAPI-based API with Swagger documentation

## 🏗️ Architecture

### Multi-Agent System

The system implements 7 specialized LangChain agents:

1. **Resume Parsing Agent**: Extracts structured data from resumes
2. **Scoring Agent**: Evaluates candidate-role fit with explainable reasoning
3. **Shortlisting Agent**: Makes threshold-based shortlist decisions
4. **Interview Evaluation Agent**: Assesses interview performance
5. **Email Agent**: Handles automated email communications
6. **Database Agent**: Manages database operations
7. **Vector Search Agent**: Performs semantic similarity searches

### Data Storage

- **MySQL**: Stores all structured business data (candidates, scores, interviews, rankings)
- **ChromaDB**: Vector database for semantic search (resume and role embeddings)

## 📋 Prerequisites

- Python 3.9+
- MySQL 8.0+
- OpenAI API key
- Gmail API credentials (OAuth2)

## 🚀 Installation

### 1. Clone the Repository

```bash
cd "HR Hiring Managment System"
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Database
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/hr_hiring_db

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Gmail API
GMAIL_CREDENTIALS_FILE=path/to/credentials.json
GMAIL_TOKEN_FILE=path/to/token.json
SENDER_EMAIL=your_email@gmail.com
```

### 5. Setup MySQL Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE hr_hiring_db;
```

### 6. Setup Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials as `credentials.json`
6. Place in your project directory

## 🎬 Running the Application

### Start the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Candidates

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/candidates/submit` | Submit new candidate with resume |
| GET | `/candidates/{id}` | Get candidate details |
| POST | `/candidates/{id}/evaluate` | Evaluate candidate for role |
| GET | `/candidates` | List candidates (with filters) |
| PUT | `/candidates/{id}/stage` | Update candidate stage |
| GET | `/candidates/{id}/scores` | Get candidate scores |

### Roles

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/roles/create` | Create new hiring role |
| GET | `/roles/{id}` | Get role details |
| GET | `/roles` | List all roles |
| POST | `/roles/{id}/shortlist` | Run shortlisting for role |
| GET | `/roles/{id}/candidates` | Get candidates for role |
| GET | `/roles/{id}/rankings` | Get final rankings |

### Interviews

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/interviews/submit` | Submit interview feedback |
| GET | `/interviews/{id}` | Get interview details |
| GET | `/interviews/{id}/evaluation` | Get AI evaluation |
| GET | `/interviews/candidate/{id}` | Get candidate interviews |
| POST | `/interviews/schedule` | Schedule interview |
| POST | `/interviews/role/{id}/generate-ranking` | Generate final ranking |
| POST | `/interviews/role/{id}/final-decision` | Make final decisions |

## 🔄 Complete Workflow Example

### 1. Create a Role

```bash
curl -X POST http://localhost:8000/roles/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "Looking for experienced Python developer with FastAPI and AI/ML experience",
    "required_skills": ["Python", "FastAPI", "LangChain", "MySQL"],
    "experience_required": 5
  }'
```

### 2. Submit Candidate

```bash
curl -X POST http://localhost:8000/candidates/submit \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "phone=1234567890" \
  -F "resume=@/path/to/resume.pdf"
```

### 3. Evaluate Candidate

```bash
curl -X POST http://localhost:8000/candidates/1/evaluate \
  -H "Content-Type: application/json" \
  -d '{"role_id": 1}'
```

### 4. Run Shortlist

```bash
curl -X POST http://localhost:8000/roles/1/shortlist
```

### 5. Submit Interview Feedback

```bash
curl -X POST http://localhost:8000/interviews/submit \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 1,
    "role_id": 1,
    "interviewer_name": "Jane Smith",
    "communication_score": 8,
    "knowledge_score": 7,
    "confidence_score": 9,
    "feedback": "Strong candidate, good communication skills"
  }'
```

### 6. Generate Final Ranking

```bash
curl -X POST http://localhost:8000/interviews/role/1/generate-ranking
```

### 7. Make Final Decision

```bash
curl -X POST "http://localhost:8000/interviews/role/1/final-decision?selections=2&waitlist=1"
```

## 🗂️ Project Structure

```
HR Hiring Managment System/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/                 # API routes
│   │   ├── candidates.py
│   │   ├── roles.py
│   │   └── interviews.py
│   ├── agents/              # LangChain agents
│   │   ├── resume_agent.py
│   │   ├── scoring_agent.py
│   │   ├── shortlist_agent.py
│   │   └── interview_agent.py
│   ├── prompts/             # System prompts
│   ├── tools/               # Agent tools
│   ├── services/            # Business logic
│   ├── db/                  # Database models
│   ├── vectorstore/         # ChromaDB client
│   ├── config/              # Configuration
│   └── utils/               # Utilities
├── data/                    # Local data storage
│   ├── resumes/
│   └── chroma/
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Configuration

### Scoring Weights

Configure in `.env`:

```env
RESUME_SCORE_WEIGHT=0.6
INTERVIEW_SCORE_WEIGHT=0.4
SHORTLIST_THRESHOLD=70
MIN_MATCH_PERCENTAGE=60
```

### File Upload Settings

```env
MAX_RESUME_SIZE_MB=5
ALLOWED_RESUME_EXTENSIONS=pdf,docx
```

## 🧪 Testing

### Run Tests

```bash
pytest tests/
```

### Test Coverage

```bash
pytest --cov=app tests/
```

## 📊 Database Schema

### Tables

- `candidates` - Candidate profiles
- `roles` - Job descriptions
- `candidate_scores` - Resume matching scores
- `interviews` - Interview feedback
- `email_logs` - Email communication tracking
- `final_rankings` - Combined rankings.

### ChromaDB Collections

- `resumes` - Resume embeddings
- `roles` - Job description embeddings

## 🔐 Security Considerations

- Store API keys securely in `.env` file
- Never commit `.env` to version control
- Use OAuth2 for Gmail API authentication
- Implement rate limiting in production
- Add authentication/authorization for API endpoints

## 🚧 Production Deployment

### Environment Setup

1. Set `DEBUG=False` in `.env`
2. Configure production database
3. Set up proper CORS origins
4. Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)

### Run with Gunicorn

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📝 License

This project is for educational and commercial use.

## 🤝 Support

For issues and questions, please create an issue in the repository.

## 🎓 Credits

Built with:
- FastAPI
- LangChain
- OpenAI GPT-4
- ChromaDB
- SQLAlchemy
- Gmail API
