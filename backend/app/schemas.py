from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List

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
    week_number: int
    meetings_attended: int
    total_sales: float
    hours_worked: float
    activities: str

class EmployeeActivityCreate(EmployeeActivityBase):
    employee_id: int

class EmployeeActivity(EmployeeActivityBase):
    id: int
    employee_id: int
    
    class Config:
        from_attributes = True

class EmployeeWithActivities(Employee):
    activities: List[EmployeeActivity] = []

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    supporting_data: Optional[dict] = None 