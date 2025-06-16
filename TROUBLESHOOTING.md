# Troubleshooting Guide

## Common Issues and Solutions

### 🔧 Backend Not Responding

**Problem**: Frontend loads but backend API calls fail or timeout.

**Symptoms**:
- Frontend loads at `http://localhost:8000`
- Query button doesn't work or shows connection errors
- Toast notifications show "Failed to execute query"

**Solutions**:

1. **Check if server is running**:
   ```bash
   ps aux | grep uvicorn
   ```

2. **Check port availability**:
   ```bash
   lsof -i :8000
   ```

3. **Kill conflicting processes**:
   ```bash
   pkill -f uvicorn
   ```

4. **Restart the server**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Test API directly**:
   ```bash
   curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "How many employees?"}'
   ```

### 🗄️ Database Connection Issues

**Problem**: Database connection errors.

**Symptoms**:
- "Database connection failed" messages
- SQL execution errors
- Server startup failures

**Solutions**:

1. **Check PostgreSQL is running**:
   ```bash
   brew services list | grep postgresql
   # or
   sudo systemctl status postgresql
   ```

2. **Test database connection**:
   ```bash
   python -c "import psycopg2; conn = psycopg2.connect(host='localhost', database='employee_tracker', user='user', password='password'); print('✅ Connected')"
   ```

3. **Recreate database if needed**:
   ```bash
   createdb -O user employee_tracker
   cd backend
   python generate_data.py
   ```

### 🔑 OpenAI API Issues

**Problem**: LLM queries fail.

**Symptoms**:
- "OpenAI API error" messages
- Queries return empty responses
- Authentication errors

**Solutions**:

1. **Check API key**:
   ```bash
   echo $OPENAI_API_KEY
   ```

2. **Set API key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Test API key**:
   ```bash
   python -c "import openai; print('✅ API key valid')"
   ```

### 🌐 Frontend Issues

**Problem**: Frontend doesn't load or looks broken.

**Symptoms**:
- Blank page at `http://localhost:8000`
- Missing styles or broken layout
- JavaScript errors in browser console

**Solutions**:

1. **Check static files**:
   ```bash
   curl -I http://localhost:8000/static/styles.css
   curl -I http://localhost:8000/static/script.js
   ```

2. **Clear browser cache**:
   - Press `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
   - Or open Developer Tools → Network → Disable cache

3. **Check browser console**:
   - Press `F12` → Console tab
   - Look for JavaScript errors

### 🚀 Quick Reset

If everything seems broken, try this complete reset:

```bash
# 1. Stop all processes
pkill -f uvicorn

# 2. Check database
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', database='employee_tracker', user='user', password='password'); print('✅ DB OK')"

# 3. Set API key
export OPENAI_API_KEY="your-api-key-here"

# 4. Restart server
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 📊 Testing Commands

**Test frontend**:
```bash
curl http://localhost:8000/
```

**Test API**:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many employees?"}'
```

**Test benchmark**:
```bash
curl -X POST "http://localhost:8000/benchmark"
```

**Run demo script**:
```bash
python demo_frontend.py
```

### 🔍 Log Analysis

**Check server logs**:
- Look at the terminal where uvicorn is running
- Check for error messages or stack traces

**Check browser network tab**:
- Press `F12` → Network tab
- Look for failed requests (red entries)
- Check response codes and error messages

### 📞 Getting Help

If issues persist:

1. **Check the logs** in the terminal running uvicorn
2. **Look at browser console** for JavaScript errors
3. **Test individual components** (database, API, frontend)
4. **Use the demo script** to isolate issues
5. **Check system requirements** (Python 3.11+, PostgreSQL 12+)

### ⚡ Performance Issues

**Slow queries**:
- Check OpenAI API status
- Monitor database performance
- Look for network connectivity issues

**High memory usage**:
- Restart the server periodically
- Check for memory leaks in logs
- Monitor system resources 