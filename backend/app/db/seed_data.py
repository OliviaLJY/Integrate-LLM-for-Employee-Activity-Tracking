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
        "Prepared sales presentation for client meeting and implemented new sales strategy",
        "Attended team training session and documented key learnings",
        "Worked on quarterly report and identified areas for improvement",
        "Conducted market research and analyzed competitor strategies",
        "Implemented new feature and resolved technical challenges",
        "Fixed critical bug in production and documented solution",
        "Met with potential clients and addressed their concerns",
        "Updated documentation and improved code quality",
        "Participated in code review and suggested optimizations",
        "Analyzed customer feedback and proposed solutions",
        "Faced challenges with customer retention and implemented new engagement strategy",
        "Prepared data analysis report for management review",
        "Led team meeting to discuss project progress and challenges",
        "Developed new marketing campaign and tracked its performance",
        "Conducted performance review and provided feedback"
    ]
    
    # Generate realistic sales data in RMB
    base_sales = random.uniform(10000, 50000)
    # Add some variation based on week number
    sales_variation = random.uniform(0.8, 1.2)
    total_sales = round(base_sales * sales_variation, 2)
    
    # Generate realistic hours (35-50 hours per week)
    hours_worked = round(random.uniform(35, 50), 1)
    
    # Generate realistic meetings (2-10 per week)
    meetings_attended = random.randint(2, 10)
    
    return {
        "employee_id": employee_id,
        "week_number": week_number,
        "meetings_attended": meetings_attended,
        "total_sales": total_sales,
        "hours_worked": hours_worked,
        "activities": random.choice(activities)
    }

def seed_database(db: Session, num_employees: int = 10, weeks: int = 10):
    """Seed the database with synthetic data"""
    # Clear existing data
    db.query(models.EmployeeActivity).delete()
    db.query(models.Employee).delete()
    db.commit()
    
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