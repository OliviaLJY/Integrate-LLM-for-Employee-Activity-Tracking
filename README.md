# Employee Activity Tracking System with LLM Integration

A comprehensive system that uses Large Language Models (LLM) to process and analyze employee activity data, providing natural language insights and summaries through a modern web interface.

## Product Demo Video  
[Click to Watch](https://drive.google.com/file/d/1sZFon6VOHJJeGvMGJYlhrCf2zHkdWukE/view?usp=drive_link)

<img width="912" alt="image" src="https://github.com/user-attachments/assets/ab27be20-a2f5-4cb0-a725-7f906dfe5e05" />

## Features

- **Natural Language Queries**: Ask questions in plain English about employee activities
- **LLM-Powered Analytics**: OpenAI GPT-4 integration for intelligent query processing
- **Modern Web Interface**: Responsive frontend with real-time query execution
- **Comprehensive Database**: PostgreSQL with 10 employees across 6 departments
- **Performance Monitoring**: 95% accuracy with benchmark testing capabilities
- **Real-time Results**: Sub-2-second query execution with formatted responses

## Tech Stack

- **Backend**: Python (FastAPI)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **LLM**: OpenAI GPT-4 with enhanced prompt engineering
- **Frontend**: Modern HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Custom CSS with Flexbox/Grid, Font Awesome icons
- **API**: RESTful endpoints with automatic documentation

## Quick Start

### Option 1: Easy Launch (Recommended)
```bash
./start_app.sh
```
Then open your browser to `http://localhost:8000`

### Option 2: Manual Setup

1. **Prerequisites**:
   - Python 3.11+
   - PostgreSQL 12+
   - OpenAI API key

2. **Database Setup**:
   ```bash
   # Create PostgreSQL user and database
   createuser -s user
   createdb -O user employee_tracker
   psql -U user -d employee_tracker -c "ALTER USER user PASSWORD 'password';"
   ```

3. **Environment Setup**:
   ```bash
   python3.11 -m venv venv_py311
   source venv_py311/bin/activate
   pip install -r backend/requirements.txt
   ```

4. **Environment Variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

5. **Initialize Database**:
   ```bash
   cd backend
   python -c "from app.db.database import engine; from app.db import models; models.Base.metadata.create_all(bind=engine)"
   python generate_data.py
   ```

6. **Start the Application**:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Usage

### Web Interface
1. Open `http://localhost:8000` in your browser
2. Use the search box to ask natural language questions
3. Click example queries for quick testing
4. View results with execution times and SQL queries

### Example Queries
- "Who worked the most hours last week?"
- "What is the total sales revenue for the Sales department?"
- "Which employees were hired during 2023?"
- "Compare hours worked by Wei Zhang and Tao Huang"

### Quick Actions
- **View All Employees**: Browse complete employee directory
- **Run Benchmark**: Execute all 20 test queries (95% accuracy)
- **Recent Activities**: View latest employee activity records

## Project Structure

```
employee-activity-tracker/
├── frontend/              # Modern web interface
│   ├── index.html        # Main HTML file
│   ├── styles.css        # CSS styling
│   ├── script.js         # JavaScript functionality
│   └── README.md         # Frontend documentation
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── db/           # Database models & connection
│   │   ├── llm/          # LLM integration & prompts
│   │   └── schemas.py    # Pydantic models
│   ├── generate_data.py  # Database population script
│   └── requirements.txt  # Python dependencies
├── start_app.sh          # Easy launch script
└── README.md            # This file
```

## Performance

- **Accuracy**: 95% (19/20 test queries correct)
- **Execution Time**: Average 1.2 seconds per query
- **Success Rate**: 100% (no failed executions)
- **Database**: 10 employees, 10 weeks of activity data

## API Documentation

Once the server is running, visit:
- **Frontend**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Common Issues
1. **Database Connection Error**: Ensure PostgreSQL is running
2. **OpenAI API Error**: Check your API key is set correctly
3. **Frontend Not Loading**: Verify server is running on port 8000

### Development
- Check browser console for JavaScript errors
- Monitor Network tab for API request/response details
- Use `curl` commands to test API endpoints directly

## License

MIT
