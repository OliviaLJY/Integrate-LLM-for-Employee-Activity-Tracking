# Employee Activity Tracking System with LLM Integration

A system that uses Large Language Models (LLM) to process and analyze employee activity data, providing natural language insights and summaries.

## Features

- SQL database for employee activity tracking
- LLM-powered natural language query processing
- Comprehensive employee activity monitoring
- Department-wise analytics
- Natural language summaries and insights

## Tech Stack

- Backend: Python (FastAPI)
- Database: PostgreSQL
- LLM: OpenAI GPT-4
- Frontend: React (coming soon)
- Authentication: JWT

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. Initialize the database:
   ```bash
   alembic upgrade head
   ```
6. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

```
employee-activity-tracker/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── db/            # Database models
│   │   ├── llm/           # LLM integration
│   │   └── services/      # Business logic
│   ├── tests/             # Backend tests
│   └── requirements.txt
└── docker/                # Docker configuration
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with:
```bash
pytest
```

## License

MIT # Integrate-LLM-for-Employee-Activity-Tracking
