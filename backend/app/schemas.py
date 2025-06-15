from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date

class EmployeeBase(BaseModel):
    email: EmailStr
    job_title: str
    department: str
    hire_date: date

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
    query: str

class QueryResponse(BaseModel):
    response: str
    confidence: float
    error: Optional[str] = None
    sql_query: Optional[str] = None

class BenchmarkResult(BaseModel):
    query: str
    response: str
    execution_time: float
    success: bool
    error: Optional[str] = None

class BenchmarkResponse(BaseModel):
    results: List[BenchmarkResult]
    total_queries: int
    successful_queries: int
    average_execution_time: float
    query_type_distribution: dict 