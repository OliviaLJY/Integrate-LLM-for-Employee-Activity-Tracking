from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import date

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    job_title = Column(String)
    department = Column(String)
    hire_date = Column(Date)
    
    # Relationships
    activities = relationship("EmployeeActivity", back_populates="employee")

class EmployeeActivity(Base):
    __tablename__ = "employee_activities"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    week_number = Column(Integer)
    meetings_attended = Column(Integer)
    total_sales = Column(Float)  # in RMB
    hours_worked = Column(Float)
    activities = Column(Text)  # Description of activities
    
    # Relationships
    employee = relationship("Employee", back_populates="activities") 