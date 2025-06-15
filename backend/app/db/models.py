from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=False)
    job_title = Column(String)
    department = Column(String)
    hire_date = Column(Date)
    
    # Relationship with activities
    activities = relationship("EmployeeActivity", back_populates="employee")

class EmployeeActivity(Base):
    __tablename__ = "employee_activities"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    week_number = Column(Integer)  # 1-10 as per requirements
    meetings_attended = Column(Integer)
    total_sales = Column(Float)  # In RMB as per requirements
    hours_worked = Column(Float)
    activities = Column(String)  # Detailed activity description
    
    # Relationship with employee
    employee = relationship("Employee", back_populates="activities")
    # NOTE: Enforce 'Sales' department total_sales logic in application code, not as a DB constraint.

class CalendarWeek(Base):
    __tablename__ = "calendar_weeks"

    week_number = Column(Integer, primary_key=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

