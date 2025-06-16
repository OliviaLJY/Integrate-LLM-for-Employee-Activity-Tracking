#!/usr/bin/env python3
"""
Demo script to showcase the Employee Activity Tracker frontend functionality
"""

import requests
import time
import json

API_BASE_URL = "http://localhost:8000"

def test_frontend_functionality():
    """Test various frontend features"""
    
    print("🎯 Employee Activity Tracker - Frontend Demo")
    print("=" * 50)
    
    # Test 1: Basic query
    print("\n1. Testing Natural Language Query...")
    query_data = {
        "query": "Who achieved the highest sales revenue in a single week?"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/query", json=query_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query: {query_data['query']}")
            print(f"📊 Response: {result['response']}")
            print(f"⏱️  Execution Time: {result.get('execution_time', 0):.3f}s")
            print(f"🔍 SQL: {result['sql_query']}")
        else:
            print(f"❌ Query failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: Employee list
    print("\n2. Testing Employee Directory...")
    try:
        response = requests.get(f"{API_BASE_URL}/employees/")
        if response.status_code == 200:
            employees = response.json()
            print(f"✅ Found {len(employees)} employees")
            for emp in employees[:3]:  # Show first 3
                print(f"   👤 {emp.get('full_name', 'N/A')} - {emp.get('job_title', 'N/A')} ({emp.get('department', 'N/A')})")
            if len(employees) > 3:
                print(f"   ... and {len(employees) - 3} more employees")
        else:
            print(f"❌ Employee list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 3: Activities
    print("\n3. Testing Recent Activities...")
    try:
        response = requests.get(f"{API_BASE_URL}/activities/?limit=5")
        if response.status_code == 200:
            activities = response.json()
            print(f"✅ Found {len(activities)} recent activities")
            for activity in activities[:2]:  # Show first 2
                print(f"   📋 Week {activity['week_number']}: {activity['hours_worked']}h worked, {activity['meetings_attended']} meetings")
        else:
            print(f"❌ Activities failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 4: Benchmark
    print("\n4. Testing Benchmark (this may take a moment)...")
    try:
        start_time = time.time()
        response = requests.post(f"{API_BASE_URL}/benchmark")
        if response.status_code == 200:
            benchmark = response.json()
            execution_time = time.time() - start_time
            print(f"✅ Benchmark completed in {execution_time:.1f}s")
            print(f"📈 Success Rate: {benchmark['successful_queries']}/{benchmark['total_queries']} ({(benchmark['successful_queries']/benchmark['total_queries']*100):.1f}%)")
            print(f"⚡ Average Query Time: {benchmark['average_execution_time']:.3f}s")
            print(f"📊 Query Types: {benchmark['query_type_distribution']}")
        else:
            print(f"❌ Benchmark failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Frontend Demo Complete!")
    print("🌐 Open http://localhost:8000 in your browser to try the web interface")
    print("📚 API docs available at http://localhost:8000/docs")
    
    return True

def check_server_status():
    """Check if the server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🔍 Checking server status...")
    
    if not check_server_status():
        print("❌ Server not running!")
        print("Please start the server first:")
        print("   ./start_app.sh")
        print("   OR")
        print("   cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
    
    print("✅ Server is running!")
    test_frontend_functionality() 