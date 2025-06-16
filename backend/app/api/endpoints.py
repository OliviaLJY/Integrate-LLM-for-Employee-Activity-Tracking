from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from ..db.database import get_db
from ..db import models
from ..schemas import (
    Employee, EmployeeCreate, EmployeeActivity, EmployeeActivityCreate,
    QueryRequest, QueryResponse, EmployeeWithActivities, BenchmarkResponse, BenchmarkResult
)
from ..llm.query_processor import process_query
import time
import re

router = APIRouter()

def format_sql_query(sql: str) -> str:
    """Format SQL query to be more readable by removing excessive newlines and normalizing spacing"""
    if not sql:
        return sql
    
    # Remove excessive whitespace and normalize
    lines = [line.strip() for line in sql.split('\n') if line.strip()]
    
    # Join with single spaces, but preserve logical breaks
    formatted_sql = ' '.join(lines)
    
    # Add strategic line breaks for better readability
    keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 
                'GROUP BY', 'ORDER BY', 'HAVING', 'UNION', 'AND', 'OR']
    
    for keyword in keywords:
        # Add line break before major keywords (except AND/OR which are inline)
        if keyword not in ['AND', 'OR']:
            formatted_sql = formatted_sql.replace(f' {keyword} ', f' {keyword} ')
    
    return formatted_sql

@router.post("/query", response_model=QueryResponse)
def process_query_endpoint(query_request: QueryRequest, db: Session = Depends(get_db)):
    """Process a natural language query about employee activities"""
    try:
        # Get SQL from LLM
        sql_query = process_query(query_request.query)
        
        # Extract SQL from response (assuming it's between <sql> and </sql> tags)
        sql_match = re.search(r'<sql>(.*?)</sql>', sql_query, re.DOTALL)
        if sql_match:
            sql = sql_match.group(1).strip()
            
            # Execute the SQL query
            try:
                result = db.execute(text(sql))
                rows = result.fetchall()
                
                # Format the results as a readable response
                if rows:
                    # Get column names
                    columns = list(result.keys())
                    
                    if len(rows) == 1:
                        # Single result - compact format
                        row = rows[0]
                        result_parts = [f"{col}: {value}" for col, value in zip(columns, row)]
                        response_text = " | ".join(result_parts)
                    else:
                        # Multiple results - structured format
                        response_text = f"Found {len(rows)} results: "
                        result_summaries = []
                        for i, row in enumerate(rows, 1):
                            # Create a compact summary for each result
                            key_info = []
                            for col, value in zip(columns, row):
                                if col in ['full_name', 'email', 'department', 'total_sales', 'hours_worked', 'meetings_attended']:
                                    key_info.append(f"{col}: {value}")
                            result_summaries.append(f"({i}) {' | '.join(key_info)}")
                        response_text += "; ".join(result_summaries)
                else:
                    response_text = "No results found for this query."
                
                return QueryResponse(
                    query=query_request.query,
                    sql_query=format_sql_query(sql),
                    response=response_text.strip(),
                    confidence=0.9,
                    error=None
                )
            except Exception as sql_error:
                db.rollback()
                return QueryResponse(
                    query=query_request.query,
                    sql_query=format_sql_query(sql),
                    response="SQL execution failed",
                    confidence=0.0,
                    error=str(sql_error)
                )
        else:
            return QueryResponse(
                query=query_request.query,
                sql_query=sql_query,
                response="Could not extract SQL from LLM response",
                confidence=0.0,
                error="SQL extraction failed"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/employees/", response_model=Employee)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """Create a new employee"""
    try:
        db_employee = models.Employee(**employee.model_dump())
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/employees/", response_model=List[Employee])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all employees"""
    try:
        employees = db.query(models.Employee).offset(skip).limit(limit).all()
        return employees
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/employees/{employee_id}", response_model=EmployeeWithActivities)
def read_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific employee with their activities"""
    try:
        employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/activities/", response_model=EmployeeActivity)
def create_activity(
    activity: EmployeeActivityCreate,
    db: Session = Depends(get_db)
):
    """Create a new activity record"""
    try:
        db_activity = models.EmployeeActivity(**activity.model_dump())
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/activities/", response_model=List[EmployeeActivity])
def read_activities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all activity records"""
    try:
        activities = db.query(models.EmployeeActivity).offset(skip).limit(limit).all()
        return activities
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/benchmark", response_model=BenchmarkResponse)
def run_benchmark(db: Session = Depends(get_db)):
    """Run benchmark tests on the query processor"""
    test_queries = [
        # Basic employee information
        "What is the email address of the employee who is the Sales Manager?",
        "Which employee in the company works in the Product Development department?",
        "What was the sales revenue of 'Wei Zhang' for the week starting on '2024-08-28'?",
        "Who are the employees working in the 'Finance' department?",
        "Retrieve the total number of meetings attended by 'Na Li' in her weekly updates.",
        
        # Hours and workload
        "Which employees worked more than 40 hours during week 1?",
        "How many employees does the company have in total?",
        "What is the average hours worked by all employees during week 2?",
        "How much total sales revenue has the Sales department generated to date?",
        "What is the total sales revenue generated by the company during week 1?",
        
        # Performance metrics
        "Who worked the most hours during the first week of September 2024?",
        "Which employee attended the most meetings during week 2?",
        "Which employees in the company were hired during a time of industry recession?",
        "Who are the employees that faced challenges with customer retention, and what solutions did they propose?",
        "Which employees work in roles that likely require data analysis or reporting skills?",
        
        # Department and comparative analysis
        "List all employees who work in the IT department within the company.",
        "Compare the hours worked by 'Wei Zhang' and 'Tao Huang' during week 1.",
        "Who are the top 3 employees by total hours worked during the last 4 weeks?",
        "Who achieved the highest sales revenue in a single week, and when?",
        "What is the total number of hours worked and average sales revenue for employees in the Business Development department?"
    ]
    
    results = []
    query_type_distribution = {}
    total_time = 0
    successful_queries = 0
    
    for query in test_queries:
        start_time = time.time()
        try:
            # Get SQL from LLM
            sql_query = process_query(query)
            
            # Extract SQL from response
            sql_match = re.search(r'<sql>(.*?)</sql>', sql_query, re.DOTALL)
            if sql_match:
                sql = sql_match.group(1).strip()
                
                # Execute the SQL query
                try:
                    result = db.execute(text(sql))
                    rows = result.fetchall()
                    
                    execution_time = time.time() - start_time
                    total_time += execution_time
                    successful_queries += 1
                    
                    # Format the results as a readable response
                    if rows:
                        # Get column names
                        columns = list(result.keys())
                        
                        if len(rows) == 1:
                            # Single result - compact format
                            row = rows[0]
                            result_parts = [f"{col}: {value}" for col, value in zip(columns, row)]
                            response_text = " | ".join(result_parts)
                        elif len(rows) <= 3:
                            # Few results - structured format
                            response_text = f"Found {len(rows)} results: "
                            result_summaries = []
                            for i, row in enumerate(rows, 1):
                                # Create a compact summary for each result
                                key_info = []
                                for col, value in zip(columns, row):
                                    if col in ['full_name', 'email', 'department', 'total_sales', 'hours_worked', 'meetings_attended']:
                                        key_info.append(f"{col}: {value}")
                                result_summaries.append(f"({i}) {' | '.join(key_info)}")
                            response_text += "; ".join(result_summaries)
                        else:
                            # Many results - show first 3 with summary
                            response_text = f"Found {len(rows)} results (showing first 3): "
                            result_summaries = []
                            for i, row in enumerate(rows[:3], 1):
                                key_info = []
                                for col, value in zip(columns, row):
                                    if col in ['full_name', 'email', 'department', 'total_sales', 'hours_worked', 'meetings_attended']:
                                        key_info.append(f"{col}: {value}")
                                result_summaries.append(f"({i}) {' | '.join(key_info)}")
                            response_text += "; ".join(result_summaries) + f" ... and {len(rows) - 3} more"
                    else:
                        response_text = "No results found for this query."
                    
                    # Simple query type determination based on keywords
                    query_type = "basic"
                    if any(word in query.lower() for word in ["total", "sum", "average", "count"]):
                        query_type = "aggregation"
                    elif any(word in query.lower() for word in ["most", "highest", "top", "best"]):
                        query_type = "ranking"
                    elif any(word in query.lower() for word in ["compare", "vs", "versus"]):
                        query_type = "comparison"
                    
                    query_type_distribution[query_type] = query_type_distribution.get(query_type, 0) + 1
                    
                    results.append(BenchmarkResult(
                        query=query,
                        response=response_text.strip(),
                        execution_time=execution_time,
                        success=True,
                        error=None,
                        sql_query=format_sql_query(sql)
                    ))
                except Exception as sql_error:
                    db.rollback()
                    execution_time = time.time() - start_time
                    results.append(BenchmarkResult(
                        query=query,
                        response="SQL execution failed",
                        execution_time=execution_time,
                        success=False,
                        error=str(sql_error),
                        sql_query=format_sql_query(sql)
                    ))
            else:
                execution_time = time.time() - start_time
                results.append(BenchmarkResult(
                    query=query,
                    response="Could not extract SQL from LLM response",
                    execution_time=execution_time,
                    success=False,
                    error="SQL extraction failed",
                    sql_query=sql_query
                ))
            
        except Exception as e:
            execution_time = time.time() - start_time
            results.append(BenchmarkResult(
                query=query,
                response="Error processing query",
                execution_time=execution_time,
                success=False,
                error=str(e)
            ))
    
    return BenchmarkResponse(
        total_queries=len(test_queries),
        successful_queries=successful_queries,
        average_execution_time=total_time / len(test_queries) if test_queries else 0,
        query_type_distribution=query_type_distribution,
        results=results
    ) 