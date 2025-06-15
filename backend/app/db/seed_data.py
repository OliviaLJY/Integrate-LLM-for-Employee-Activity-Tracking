from faker import Faker
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
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

def seed_calendar_weeks(db: Session):
    """Seed calendar weeks for 2024"""
    start_date = datetime(2024, 1, 1)
    for week in range(1, 11):
        week_start = start_date + timedelta(days=(week-1)*7)
        week_end = week_start + timedelta(days=6)
        calendar_week = models.CalendarWeek(
            week_number=week,
            start_date=week_start.date(),
            end_date=week_end.date()
        )
        db.add(calendar_week)
    db.commit()

def seed_employees(db: Session):
    """Seed employee data with all departments, job titles, and names referenced in queries"""
    employees = [
        # Sales
        {"email": "leroyrussell@example.org", "full_name": "Leroy Russell", "job_title": "Sales Manager", "department": "Sales", "hire_date": datetime(2023, 1, 15).date()},
        {"email": "weizhang@example.com", "full_name": "Wei Zhang", "job_title": "Sales Representative", "department": "Sales", "hire_date": datetime(2023, 3, 10).date()},
        {"email": "samanthataylor@example.net", "full_name": "Samantha Taylor", "job_title": "Account Executive", "department": "Sales", "hire_date": datetime(2024, 6, 1).date()},
        # IT
        {"email": "nataliechen@example.net", "full_name": "Natalie Chen", "job_title": "Network Engineer", "department": "IT", "hire_date": datetime(2024, 2, 1).date()},
        {"email": "ssullivan@example.net", "full_name": "Sarah Sullivan", "job_title": "System Administrator", "department": "IT", "hire_date": datetime(2024, 3, 15).date()},
        {"email": "foneill@example.org", "full_name": "Frank O'Neill", "job_title": "IT Manager", "department": "IT", "hire_date": datetime(2024, 4, 1).date()},
        {"email": "ocooper@example.com", "full_name": "Oliver Cooper", "job_title": "Network Engineer", "department": "IT", "hire_date": datetime(2024, 8, 1).date()},
        # Product Development
        {"email": "aprilmartinez@example.net", "full_name": "April Martinez", "job_title": "UX Designer", "department": "Product Development", "hire_date": datetime(2023, 9, 21).date()},
        {"email": "kimlee@example.com", "full_name": "Kim Lee", "job_title": "Software Engineer", "department": "Product Development", "hire_date": datetime(2024, 9, 29).date()},
        {"email": "taohuang@example.com", "full_name": "Tao Huang", "job_title": "Product Manager", "department": "Product Development", "hire_date": datetime(2024, 5, 10).date()},
        # Marketing
        {"email": "michellewang@example.net", "full_name": "Michelle Wang", "job_title": "Marketing Specialist", "department": "Marketing", "hire_date": datetime(2024, 7, 1).date()},
        {"email": "patriciaglover@example.com", "full_name": "Patricia Glover", "job_title": "Marketing Manager", "department": "Marketing", "hire_date": datetime(2024, 5, 1).date()},
        # Finance
        {"email": "nalifinance@example.com", "full_name": "Na Li", "job_title": "Finance Manager", "department": "Finance", "hire_date": datetime(2023, 12, 1).date()},
        {"email": "frankwong@example.com", "full_name": "Frank Wong", "job_title": "Accountant", "department": "Finance", "hire_date": datetime(2024, 1, 20).date()},
        # Business Development
        {"email": "danielzhang@example.com", "full_name": "Daniel Zhang", "job_title": "Business Analyst", "department": "Business Development", "hire_date": datetime(2024, 2, 15).date()},
        {"email": "lucyliu@example.com", "full_name": "Lucy Liu", "job_title": "Data Analyst", "department": "Business Development", "hire_date": datetime(2024, 3, 5).date()},
    ]
    for employee_data in employees:
        employee = models.Employee(**employee_data)
        db.add(employee)
    db.commit()

def seed_activities(db: Session):
    """Seed employee activity data with realistic metrics and varied activities"""
    activities = [
        "Prepared and presented quarterly sales report",
        "Led team meeting to discuss project progress and challenges",
        "Implemented new feature and resolved technical challenges",
        "Conducted customer training session",
        "Faced challenges with customer retention and implemented new engagement strategy",
        "Created and delivered product demonstration",
        "Resolved critical system outage",
        "Developed new marketing campaign",
        "Optimized database performance",
        "Conducted code review and provided feedback",
        "Prepared data analysis report for management review",
        "Worked on data analysis and reporting tasks",
        "Analyzed customer feedback and proposed solutions",
        "Faced challenges with data quality and implemented solutions",
        "Worked on business development strategy and client acquisition"
    ]
    
    # Base metrics by department
    department_metrics = {
        "Sales": {
            "hours_range": (40, 50),
            "sales_range": (30000, 100000),
            "meetings_range": (5, 12)
        },
        "IT": {
            "hours_range": (35, 45),
            "sales_range": (0, 0),
            "meetings_range": (3, 8)
        },
        "Finance": {
            "hours_range": (38, 45),
            "sales_range": (0, 0),
            "meetings_range": (4, 10)
        },
        "Marketing": {
            "hours_range": (35, 45),
            "sales_range": (0, 0),
            "meetings_range": (4, 10)
        },
        "Product Development": {
            "hours_range": (40, 48),
            "sales_range": (0, 0),
            "meetings_range": (3, 8)
        },
        "Business Development": {
            "hours_range": (38, 45),
            "sales_range": (20000, 80000),
            "meetings_range": (5, 12)
        }
    }
    
    employees = db.query(models.Employee).all()
    for employee in employees:
        metrics = department_metrics[employee.department]
        for week in range(1, 11):
            # Add some weekly variation
            week_factor = 0.9 + (week % 3) * 0.1  # 0.9 to 1.1
            
            hours = round(random.uniform(*metrics["hours_range"]) * week_factor, 1)
            sales = round(random.uniform(*metrics["sales_range"]) * week_factor, 2) if metrics["sales_range"][1] > 0 else None
            meetings = random.randint(*metrics["meetings_range"])
            
            activity = models.EmployeeActivity(
                employee_id=employee.id,
                week_number=week,
                meetings_attended=meetings,
                total_sales=sales,
                hours_worked=hours,
                activities=random.choice(activities)
            )
            db.add(activity)
    db.commit()

def seed_database(db: Session):
    """Seed all database tables"""
    seed_calendar_weeks(db)
    seed_employees(db)
    seed_activities(db)

if __name__ == "__main__":
    from .database import SessionLocal
    db = SessionLocal()
    try:
        seed_database(db)
        print("Database seeded successfully!")
    finally:
        db.close() 