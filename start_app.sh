#!/bin/bash

# Employee Activity Tracker - Launch Script
echo "🚀 Starting Employee Activity Tracker..."
echo "========================================="

# Check if virtual environment exists
if [ ! -d "venv_py311" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv_py311/bin/activate

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python -c "import fastapi, sqlalchemy, openai, psycopg2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r backend/requirements.txt
fi

# Check if PostgreSQL is running
echo "🗄️  Checking PostgreSQL connection..."
python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='employee_tracker',
        user='user',
        password='password'
    )
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('Please ensure PostgreSQL is running and database is set up.')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Start the application
echo "🌐 Starting FastAPI server..."
echo "Frontend will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="

cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 