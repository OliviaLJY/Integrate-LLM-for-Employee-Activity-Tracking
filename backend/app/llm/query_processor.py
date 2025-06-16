from openai import OpenAI

client = OpenAI()

def process_query(query: str) -> str:
    """Process natural language query and return SQL"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a PostgreSQL SQL expert. Generate PostgreSQL-compatible SQL queries only.\n\nDatabase Schema:\n        \n        Table: employees\n        - id (INTEGER, PRIMARY KEY)\n        - email (VARCHAR)\n        - full_name (VARCHAR, NOT NULL)\n        - department (VARCHAR) - Values: Sales, Marketing, Product Development, Finance, IT, Business Development\n        - job_title (VARCHAR) - e.g., Sales Manager, Data Analyst, Marketing Specialist\n        - hire_date (DATE)\n        \n        Table: employee_activities  \n        - id (INTEGER, PRIMARY KEY)\n        - employee_id (INTEGER, FOREIGN KEY to employees.id)\n        - week_number (INTEGER, 1-10)\n        - hours_worked (DECIMAL)\n        - total_sales (DECIMAL) - in RMB\n        - meetings_attended (INTEGER)\n        - activities (TEXT) - descriptions of work activities\n        \n        Table: calendar_weeks\n        - week_number (INTEGER, PRIMARY KEY)\n        - start_date (DATE, NOT NULL)\n        - end_date (DATE, NOT NULL)\n        \n        PostgreSQL Syntax Rules:\n        1. Use INTERVAL '4 weeks' not INTERVAL 4 WEEK\n        2. Use CURRENT_DATE not DATE(NOW())\n        3. Use proper PostgreSQL date functions\n        4. Always use single quotes for string literals\n        5. Use proper PostgreSQL aggregate functions\n        \n        Critical Rules:\n        1. Always use full_name for employee lookups\n        2. Join calendar_weeks for date-based queries\n        3. Format numbers with proper units (RMB, hours)\n        4. Validate departments before querying\n        5. Handle missing data gracefully\n        6. Generate ONLY PostgreSQL-compatible SQL\n        7. For 'last 4 weeks' queries, use week_number >= 7 (since we have weeks 1-10)\n\nGenerate the SQL query to answer the following question. Put the SQL query between <sql> and </sql>"
            },
            {
                "role": "user",
                "content": query
            }
        ],
        temperature=0.1,
        max_tokens=2048
    )
    
    return response.choices[0].message.content 