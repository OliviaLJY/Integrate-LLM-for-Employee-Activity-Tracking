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
    """Seed calendar weeks for 2024 (10 weeks starting from August)"""
    # Start from August 26, 2024 to match query requirements
    start_date = datetime(2024, 8, 26)
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
    """Seed 10 employees with realistic data matching query requirements"""
    employees = [
        # Sales Department
        {
            "email": "wei.zhang@company.com",
            "full_name": "Wei Zhang",
            "job_title": "Sales Manager",
            "department": "Sales",
            "hire_date": datetime(2022, 3, 15).date()  # Pre-recession hire
        },
        {
            "email": "sarah.johnson@company.com", 
            "full_name": "Sarah Johnson",
            "job_title": "Sales Representative",
            "department": "Sales",
            "hire_date": datetime(2023, 8, 10).date()  # During recession
        },
        
        # IT Department
        {
            "email": "mike.chen@company.com",
            "full_name": "Mike Chen", 
            "job_title": "IT Manager",
            "department": "IT",
            "hire_date": datetime(2021, 11, 5).date()
        },
        {
            "email": "lisa.wang@company.com",
            "full_name": "Lisa Wang",
            "job_title": "System Administrator", 
            "department": "IT",
            "hire_date": datetime(2023, 6, 20).date()  # During recession
        },
        
        # Finance Department
        {
            "email": "na.li@company.com",
            "full_name": "Na Li",
            "job_title": "Finance Manager",
            "department": "Finance", 
            "hire_date": datetime(2022, 1, 8).date()
        },
        {
            "email": "david.kim@company.com",
            "full_name": "David Kim",
            "job_title": "Financial Analyst",
            "department": "Finance",
            "hire_date": datetime(2023, 9, 12).date()  # During recession
        },
        
        # Product Development Department
        {
            "email": "tao.huang@company.com",
            "full_name": "Tao Huang", 
            "job_title": "Product Manager",
            "department": "Product Development",
            "hire_date": datetime(2022, 7, 3).date()
        },
        {
            "email": "emma.rodriguez@company.com",
            "full_name": "Emma Rodriguez",
            "job_title": "Software Engineer",
            "department": "Product Development", 
            "hire_date": datetime(2023, 4, 18).date()  # During recession
        },
        
        # Marketing Department
        {
            "email": "alex.thompson@company.com",
            "full_name": "Alex Thompson",
            "job_title": "Marketing Specialist",
            "department": "Marketing",
            "hire_date": datetime(2022, 9, 25).date()
        },
        
        # Business Development Department
        {
            "email": "jennifer.lee@company.com",
            "full_name": "Jennifer Lee",
            "job_title": "Data Analyst", 
            "department": "Business Development",
            "hire_date": datetime(2023, 2, 14).date()  # During recession
        }
    ]
    
    for employee_data in employees:
        employee = models.Employee(**employee_data)
        db.add(employee)
    db.commit()

def get_department_activities(department: str, week: int) -> list:
    """Get realistic activities based on department and week"""
    
    sales_activities = [
        "Conducted client presentations and negotiated contract terms with major prospects",
        "Developed comprehensive sales strategy focusing on customer retention and acquisition", 
        "Faced challenges with customer retention due to competitive pricing, implemented loyalty program",
        "Prepared quarterly sales forecasts and analyzed market trends for strategic planning",
        "Led team training on new CRM system and sales methodologies",
        "Attended industry conference and established new business partnerships",
        "Resolved customer complaints and implemented service improvement initiatives",
        "Conducted market research on competitor strategies and pricing models",
        "Prepared detailed sales reports and presented findings to executive team",
        "Implemented new lead qualification process to improve conversion rates"
    ]
    
    it_activities = [
        "Upgraded server infrastructure and implemented security patches across all systems",
        "Resolved critical network outage affecting 200+ users, documented incident response",
        "Developed automated backup procedures and disaster recovery protocols", 
        "Conducted security audit and implemented multi-factor authentication system",
        "Migrated legacy applications to cloud infrastructure, reducing operational costs",
        "Provided technical support and training to staff on new software implementations",
        "Optimized database performance resulting in 40% improvement in query response times",
        "Implemented monitoring tools for proactive system maintenance and alerting",
        "Led cybersecurity awareness training sessions for all departments",
        "Designed and deployed new network architecture for remote work capabilities"
    ]
    
    finance_activities = [
        "Prepared comprehensive quarterly financial statements and variance analysis reports",
        "Conducted budget planning sessions with department heads for next fiscal year",
        "Implemented new expense tracking system to improve cost control and reporting",
        "Analyzed cash flow patterns and developed strategies for working capital optimization", 
        "Prepared tax documentation and coordinated with external auditors for compliance",
        "Developed financial models for new product launch cost-benefit analysis",
        "Conducted risk assessment and implemented internal controls for fraud prevention",
        "Prepared board presentation on financial performance and strategic recommendations",
        "Analyzed departmental spending patterns and identified cost reduction opportunities",
        "Implemented automated invoice processing system reducing processing time by 60%"
    ]
    
    product_activities = [
        "Led user research sessions and analyzed feedback to inform product roadmap decisions",
        "Developed technical specifications for new feature implementation and testing protocols",
        "Conducted competitive analysis and market research for product positioning strategy",
        "Collaborated with engineering team on sprint planning and agile development processes",
        "Designed user interface mockups and conducted usability testing with focus groups",
        "Implemented A/B testing framework to optimize user engagement and conversion rates",
        "Prepared product launch strategy and coordinated cross-functional team efforts",
        "Analyzed user analytics data to identify improvement opportunities and feature gaps",
        "Developed product documentation and training materials for customer support team",
        "Led stakeholder meetings to align product vision with business objectives"
    ]
    
    marketing_activities = [
        "Developed integrated marketing campaign across digital and traditional channels",
        "Analyzed customer segmentation data and created targeted messaging strategies",
        "Managed social media presence and increased engagement rates by 35%",
        "Coordinated with design team on brand guidelines and marketing collateral creation",
        "Conducted market research surveys and analyzed consumer behavior patterns",
        "Implemented marketing automation workflows for lead nurturing and conversion",
        "Prepared marketing performance reports and ROI analysis for campaign optimization",
        "Organized and executed trade show participation and lead generation activities",
        "Developed content marketing strategy including blog posts and white papers",
        "Collaborated with sales team on lead qualification and handoff processes"
    ]
    
    business_dev_activities = [
        "Analyzed market trends and prepared strategic recommendations for business expansion",
        "Developed partnership agreements and negotiated terms with potential collaborators",
        "Conducted financial modeling and feasibility studies for new market opportunities",
        "Prepared comprehensive business cases for new product development initiatives",
        "Led cross-functional teams in process improvement and operational efficiency projects",
        "Analyzed customer data to identify upselling and cross-selling opportunities",
        "Developed key performance indicators and reporting dashboards for executive team",
        "Conducted competitive intelligence research and market positioning analysis",
        "Facilitated strategic planning sessions and documented action items and timelines",
        "Implemented data-driven decision making processes across multiple departments"
    ]
    
    activities_map = {
        "Sales": sales_activities,
        "IT": it_activities, 
        "Finance": finance_activities,
        "Product Development": product_activities,
        "Marketing": marketing_activities,
        "Business Development": business_dev_activities
    }
    
    return activities_map.get(department, sales_activities)

def seed_activities(db: Session):
    """Seed realistic employee activity data for 10 weeks"""
    
    # Department-specific metrics for realistic data generation
    department_metrics = {
        "Sales": {
            "hours_range": (42, 55),  # Sales often work longer hours
            "sales_range": (25000, 120000),  # High variation in sales
            "meetings_range": (8, 15)  # Lots of client meetings
        },
        "IT": {
            "hours_range": (38, 48),
            "sales_range": (0, 0),  # No direct sales
            "meetings_range": (4, 8)  # Fewer meetings, more heads-down work
        },
        "Finance": {
            "hours_range": (40, 50),  # Busy during reporting periods
            "sales_range": (0, 0),
            "meetings_range": (6, 12)  # Many stakeholder meetings
        },
        "Product Development": {
            "hours_range": (40, 50),
            "sales_range": (0, 0),
            "meetings_range": (5, 10)  # Sprint meetings, standups
        },
        "Marketing": {
            "hours_range": (38, 46),
            "sales_range": (0, 0),
            "meetings_range": (6, 11)  # Campaign planning meetings
        },
        "Business Development": {
            "hours_range": (42, 52),
            "sales_range": (15000, 85000),  # Some sales component
            "meetings_range": (7, 14)  # Lots of strategic meetings
        }
    }
    
    employees = db.query(models.Employee).all()
    
    for employee in employees:
        metrics = department_metrics[employee.department]
        activities_list = get_department_activities(employee.department, 1)
        
        for week in range(1, 11):
            # Add realistic weekly variations
            if week in [1, 2]:  # First weeks might be slower
                week_factor = random.uniform(0.85, 0.95)
            elif week in [9, 10]:  # End of period push
                week_factor = random.uniform(1.05, 1.15)
            else:
                week_factor = random.uniform(0.95, 1.05)
            
            # Generate hours worked
            base_hours = random.uniform(*metrics["hours_range"])
            hours_worked = round(base_hours * week_factor, 1)
            
            # Generate sales (only for sales and business development)
            if metrics["sales_range"][1] > 0:
                base_sales = random.uniform(*metrics["sales_range"])
                # Add some employees with exceptional performance
                if employee.full_name == "Wei Zhang" and week == 3:  # High performer
                    base_sales *= 1.5
                total_sales = round(base_sales * week_factor, 2)
            else:
                total_sales = None
            
            # Generate meetings
            base_meetings = random.randint(*metrics["meetings_range"])
            meetings_attended = max(1, int(base_meetings * week_factor))
            
            # Select appropriate activity
            activity_text = random.choice(activities_list)
            
            activity = models.EmployeeActivity(
                employee_id=employee.id,
                week_number=week,
                meetings_attended=meetings_attended,
                total_sales=total_sales,
                hours_worked=hours_worked,
                activities=activity_text
            )
            db.add(activity)
    
    db.commit()

def clear_existing_data(db: Session):
    """Clear existing data before seeding"""
    db.query(models.EmployeeActivity).delete()
    db.query(models.Employee).delete() 
    db.query(models.CalendarWeek).delete()
    db.commit()

def seed_database(db: Session):
    """Seed all database tables with comprehensive realistic data"""
    print("Clearing existing data...")
    clear_existing_data(db)
    
    print("Seeding calendar weeks...")
    seed_calendar_weeks(db)
    
    print("Seeding employees...")
    seed_employees(db)
    
    print("Seeding activities...")
    seed_activities(db)
    
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    from .database import SessionLocal
    db = SessionLocal()
    try:
        seed_database(db)
        print("✅ Database seeded successfully with 10 employees over 10 weeks!")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close() 