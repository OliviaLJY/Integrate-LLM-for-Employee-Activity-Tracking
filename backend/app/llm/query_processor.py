from openai import OpenAI

client = OpenAI()

def process_query(query: str) -> str:
    """Process natural language query and return SQL"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are a PostgreSQL SQL expert. Generate PostgreSQL-compatible SQL queries only.

Database Schema:
        
Table: employees
- id (INTEGER, PRIMARY KEY)
- email (VARCHAR)
- full_name (VARCHAR, NOT NULL)
- department (VARCHAR) - Values: Sales, Marketing, Product Development, Finance, IT, Business Development
- job_title (VARCHAR) - e.g., Sales Manager, Data Analyst, Marketing Specialist
- hire_date (DATE)

Table: employee_activities  
- id (INTEGER, PRIMARY KEY)
- employee_id (INTEGER, FOREIGN KEY to employees.id)
- week_number (INTEGER, 1-10)
- hours_worked (DECIMAL)
- total_sales (DECIMAL) - in RMB (NULL for non-sales roles)
- meetings_attended (INTEGER)
- activities (TEXT) - descriptions of work activities

Table: calendar_weeks
- week_number (INTEGER, PRIMARY KEY)
- start_date (DATE, NOT NULL) - Week 1 starts 2024-08-26
- end_date (DATE, NOT NULL)

CRITICAL RULES FOR ACCURACY:

1. DATE HANDLING:
   - Week 1: 2024-08-26 to 2024-09-01
   - Week 2: 2024-09-02 to 2024-09-08 (first week of September)
   - For "week starting on YYYY-MM-DD", find week where start_date <= date <= end_date
   - For "first week of September 2024", use week containing September 1st

2. NULL VALUE HANDLING:
   - ALWAYS filter out NULL sales with "WHERE total_sales IS NOT NULL" when ordering by sales
   - Use COALESCE() for aggregations to handle NULLs properly

3. TEXT SEARCH PATTERNS:
   - For "customer retention", use: activities ILIKE '%retention%' (single condition)
   - Don't require multiple keywords with AND - use OR for flexibility
   - Use ILIKE for case-insensitive matching

4. DATE RANGE QUERIES:
   - "Industry recession" = full year 2023: hire_date >= '2023-01-01' AND hire_date <= '2023-12-31'
   - Don't use narrow date ranges unless specifically requested

5. AGGREGATION QUERIES:
   - Always use proper GROUP BY for employee-level aggregations
   - Use SUM() for totals, AVG() for averages, COUNT() for counts

6. RANKING QUERIES:
   - Always use ORDER BY with LIMIT for "top N" or "highest/most"
   - Filter NULL values BEFORE ordering when dealing with sales data

EXAMPLES:
- "Week starting 2024-08-28" → WHERE cw.start_date <= '2024-08-28' AND cw.end_date >= '2024-08-28'
- "First week of September 2024" → WHERE cw.start_date <= '2024-09-01' AND cw.end_date >= '2024-09-01'
- "Highest sales revenue" → WHERE total_sales IS NOT NULL ORDER BY total_sales DESC LIMIT 1
- "Customer retention" → WHERE activities ILIKE '%retention%'
- "Recession hires" → WHERE hire_date >= '2023-01-01' AND hire_date <= '2023-12-31'

Generate the SQL query to answer the following question. Put the SQL query between <sql> and </sql>"""
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