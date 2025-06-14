from faker import Faker
from sqlalchemy.orm import Session
from datetime import date, timedelta
import random
from . import models

fake = Faker()

def generate_employee_data():
    """Generate synthetic employee data"""
    departments = ["Sales", "Marketing", "Product Development", "Finance", "IT"]
    job_titles = {
        "Sales": ["Sales Manager", "Sales Representative", "Account Executive"],
        "Marketing": ["Marketing Manager", "Marketing Specialist", "Content Writer"],
        "Product Development": ["Product Manager", "Software Engineer", "UX Designer"],
        "Finance": ["Financial Analyst", "Accountant", "Finance Manager"],
        "IT": ["IT Manager", "System Administrator", "Network Engineer"]
    }
    
    department = random.choice(departments)
    return {
        "email": fake.email(),
        "job_title": random.choice(job_titles[department]),
        "department": department,
        "hire_date": fake.date_between(start_date="-2y", end_date="today")
    }

def generate_activity_data(employee_id: int, week_number: int):
    """Generate synthetic activity data for an employee"""
    activities = [
        "Prepared sales presentation for client meeting",
        "Attended team training session",
        "Worked on quarterly report",
        "Conducted market research",
        "Implemented new feature",
        "Fixed critical bug in production",
        "Met with potential clients",
        "Updated documentation",
        "Participated in code review",
        "Analyzed customer feedback"
    ]
    
    return {
        "employee_id": employee_id,
        "week_number": week_number,
        "meetings_attended": random.randint(2, 10),
        "total_sales": round(random.uniform(1000, 50000), 2),
        "hours_worked": round(random.uniform(35, 50), 1),
        "activities": random.choice(activities)
    }

def seed_database(db: Session, num_employees: int = 10, weeks: int = 10):
    """Seed the database with synthetic data"""
    # Generate employees
    employees = []
    for _ in range(num_employees):
        employee_data = generate_employee_data()
        db_employee = models.Employee(**employee_data)
        db.add(db_employee)
        employees.append(db_employee)
    
    db.commit()
    
    # Generate activities for each employee
    for employee in employees:
        for week in range(1, weeks + 1):
            activity_data = generate_activity_data(employee.id, week)
            db_activity = models.EmployeeActivity(**activity_data)
            db.add(db_activity)
    
    db.commit()

if __name__ == "__main__":
    from .database import SessionLocal
    db = SessionLocal()
    try:
        seed_database(db)
        print("Database seeded successfully!")
    finally:
        db.close() 