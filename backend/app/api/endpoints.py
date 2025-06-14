from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db.database import get_db
from ..db import models
from ..schemas import (
    Employee, EmployeeCreate, EmployeeActivity, EmployeeActivityCreate,
    QueryRequest, QueryResponse, EmployeeWithActivities
)
from ..llm.query_processor import QueryProcessor

router = APIRouter()
query_processor = QueryProcessor()

@router.post("/query", response_model=QueryResponse)
async def process_query(
    query_request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Process a natural language query about employee activities"""
    return query_processor.process_query(db, query_request)

@router.post("/employees/", response_model=Employee)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """Create a new employee"""
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.get("/employees/", response_model=List[Employee])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all employees"""
    employees = db.query(models.Employee).offset(skip).limit(limit).all()
    return employees

@router.get("/employees/{employee_id}", response_model=EmployeeWithActivities)
def read_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific employee with their activities"""
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.post("/activities/", response_model=EmployeeActivity)
def create_activity(
    activity: EmployeeActivityCreate,
    db: Session = Depends(get_db)
):
    """Create a new activity record"""
    db_activity = models.EmployeeActivity(**activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.get("/activities/", response_model=List[EmployeeActivity])
def read_activities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all activity records"""
    activities = db.query(models.EmployeeActivity).offset(skip).limit(limit).all()
    return activities 