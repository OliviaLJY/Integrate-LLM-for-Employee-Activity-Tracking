from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class EmployeeBase(BaseModel):
    email: EmailStr
    job_title: str
    department: str
    hire_date: datetime

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    
    class Config:
        from_attributes = True

class EmployeeActivityBase(BaseModel):
    employee_id: int
    week_number: int  # 1-10
    meetings_attended: int
    total_sales: float  # In RMB
    hours_worked: float
    activities: str  # Detailed activity description

class EmployeeActivityCreate(EmployeeActivityBase):
    pass

class EmployeeActivity(EmployeeActivityBase):
    id: int
    
    class Config:
        from_attributes = True

class EmployeeWithActivities(Employee):
    activities: List[EmployeeActivity] = []

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query about employee activities")

class QueryResponse(BaseModel):
    response: str = Field(..., description="Natural language response to the query")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the response")
    sql_query: Optional[str] = Field(None, description="SQL query used to generate the response")
    error: Optional[str] = Field(None, description="Error message if query processing failed")

class BenchmarkResult(BaseModel):
    query: str = Field(..., description="The test query")
    response: str = Field(..., description="The system's response")
    execution_time: float = Field(..., description="Time taken to process the query in seconds")
    success: bool = Field(..., description="Whether the query was processed successfully")
    error: Optional[str] = Field(None, description="Error message if query failed")
    sql_query: Optional[str] = Field(None, description="SQL query used to generate the response")

class BenchmarkResponse(BaseModel):
    total_queries: int = Field(..., description="Total number of queries tested")
    successful_queries: int = Field(..., description="Number of successfully processed queries")
    average_execution_time: float = Field(..., description="Average execution time in seconds")
    query_type_distribution: Dict[str, int] = Field(..., description="Distribution of query types")
    results: List[BenchmarkResult] = Field(..., description="Detailed results for each query") 