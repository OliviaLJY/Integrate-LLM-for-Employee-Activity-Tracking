# 20 Example Queries - SQL Reference & Commands

This document provides the correct SQL queries and commands for all 20 example queries from request.md.

## Database Schema Reference
```sql
-- employees table
- id (INTEGER, PRIMARY KEY)
- email (VARCHAR)
- full_name (VARCHAR, NOT NULL)
- department (VARCHAR) - Values: Sales, Marketing, Product Development, Finance, IT, Business Development
- job_title (VARCHAR)
- hire_date (DATE)

-- employee_activities table
- id (INTEGER, PRIMARY KEY)
- employee_id (INTEGER, FOREIGN KEY)
- week_number (INTEGER, 1-10)
- hours_worked (DECIMAL)
- total_sales (DECIMAL) - in RMB
- meetings_attended (INTEGER)
- activities (TEXT)

-- calendar_weeks table
- week_number (INTEGER, PRIMARY KEY)
- start_date (DATE, NOT NULL)
- end_date (DATE, NOT NULL)
```

---

## **Query 1: What is the email address of the employee who is the Sales Manager?**

**SQL Query:**
```sql
SELECT email, full_name 
FROM employees 
WHERE job_title = 'Sales Manager';
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the email address of the employee who is the Sales Manager?"}'
```

---

## **Query 2: Which employee in the company works in the Product Development department?**

**SQL Query:**
```sql
SELECT full_name, job_title, email 
FROM employees 
WHERE department = 'Product Development';
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Which employee in the company works in the Product Development department?"}'
```

---

## **Query 3: What was the sales revenue of 'Wei Zhang' for the week starting on '2024-08-28'?**

**SQL Query:**
```sql
SELECT e.full_name, ea.total_sales, cw.start_date, cw.end_date
FROM employees e
JOIN employee_activities ea ON e.id = ea.employee_id
JOIN calendar_weeks cw ON ea.week_number = cw.week_number
WHERE e.full_name = 'Wei Zhang' 
  AND cw.start_date <= '2024-08-28' 
  AND cw.end_date >= '2024-08-28';
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What was the sales revenue of '\''Wei Zhang'\'' for the week starting on '\''2024-08-28'\''?"}'
```

---

## **Query 4: Who are the employees working in the 'Finance' department?**

**SQL Query:**
```sql
SELECT full_name, job_title, email 
FROM employees 
WHERE department = 'Finance';
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who are the employees working in the '\''Finance'\'' department?"}'
```

---

## **Query 5: Retrieve the total number of meetings attended by 'Na Li' in her weekly updates.**

**SQL Query:**
```sql
SELECT e.full_name, SUM(ea.meetings_attended) as total_meetings
FROM employees e
JOIN employee_activities ea ON e.id = ea.employee_id
WHERE e.full_name = 'Na Li'
GROUP BY e.full_name;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Retrieve the total number of meetings attended by '\''Na Li'\'' in her weekly updates."}'
```

---

## **Query 6: Which employees worked more than 40 hours during week 1?**

**SQL Query:**
```sql
SELECT e.full_name, ea.hours_worked
FROM employees e
JOIN employee_activities ea ON e.id = ea.employee_id
WHERE ea.week_number = 1 AND ea.hours_worked > 40
ORDER BY ea.hours_worked DESC;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Which employees worked more than 40 hours during week 1?"}'
```

---

## **Query 7: How many employees does the company have in total?**

**SQL Query:**
```sql
SELECT COUNT(*) as total_employees 
FROM employees;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many employees does the company have in total?"}'
```

---

## **Query 8: What is the average hours worked by all employees during week 2?**

**SQL Query:**
```sql
SELECT AVG(hours_worked) as average_hours
FROM employee_activities
WHERE week_number = 2;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the average hours worked by all employees during week 2?"}'
```

---

## **Query 9: How much total sales revenue has the Sales department generated to date?**

**SQL Query:**
```sql
SELECT SUM(ea.total_sales) as total_sales_revenue
FROM employees e
JOIN employee_activities ea ON e.id = ea.employee_id
WHERE e.department = 'Sales' AND ea.total_sales IS NOT NULL;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How much total sales revenue has the Sales department generated to date?"}'
```

---

## **Query 10: What is the total sales revenue generated by the company during week 1?**

**SQL Query:**
```sql
SELECT SUM(total_sales) as total_week1_sales
FROM employee_activities
WHERE week_number = 1 AND total_sales IS NOT NULL;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the total sales revenue generated by the company during week 1?"}'
```

---

## **Query 11: Who worked the most hours during the first week of September 2024?**

**SQL Query:**
```sql
SELECT e.full_name, ea.hours_worked, cw.start_date
FROM employees e
JOIN employee_activities ea ON e.id = ea.employee_id
JOIN calendar_weeks cw ON ea.week_number = cw.week_number
WHERE cw.start_date >= '2024-09-01' AND cw.start_date < '2024-09-08'
ORDER BY ea.hours_worked DESC
LIMIT 1;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who worked the most hours during the first week of September 2024?"}'
```

---

## **Query 12: Which employee attended the most meetings during week 2?**

**SQL Query:**
```sql
SELECT e.full_name, ea.meetings_attended
FROM employees e
JOIN employee_activities ea ON e.id = ea.employee_id
WHERE ea.week_number = 2
ORDER BY ea.meetings_attended DESC
LIMIT 1;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Which employee attended the most meetings during week 2?"}'
```

---

## **Query 13: Which employees in the company were hired during a time of industry recession?**

**SQL Query:**
```sql
SELECT full_name, hire_date, department, job_title
FROM employees
WHERE hire_date >= '2023-01-01' AND hire_date <= '2023-12-31'
ORDER BY hire_date;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Which employees in the company were hired during a time of industry recession?"}'
```

---

## **Query 14: Who are the employees that faced challenges with customer retention, and what solutions did they propose?**

**SQL Query:**
```sql
SELECT e.full_name, ea.activities, ea.week_number
FROM employees e
JOIN employee_activities ea ON e.id = ea.employee_id
WHERE ea.activities ILIKE '%customer retention%' 
   OR ea.activities ILIKE '%retention%'
ORDER BY e.full_name, ea.week_number;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who are the employees that faced challenges with customer retention, and what solutions did they propose?"}'
```

---

## **Query 15: Which employees work in roles that likely require data analysis or reporting skills?**

**SQL Query:**
```sql
SELECT full_name, job_title, department
FROM employees
WHERE job_title ILIKE '%analyst%' 
   OR job_title ILIKE '%data%'
   OR job_title ILIKE '%report%'
   OR job_title ILIKE '%financial%'
ORDER BY department, full_name;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Which employees work in roles that likely require data analysis or reporting skills?"}'
```

---

## **Query 16: List all employees who work in the IT department within the company.**

**SQL Query:**
```sql
SELECT full_name, job_title, email, hire_date
FROM employees
WHERE department = 'IT'
ORDER BY full_name;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "List all employees who work in the IT department within the company."}'
```

---

## **Query 17: Compare the hours worked by 'Wei Zhang' and 'Tao Huang' during week 1.**

**SQL Query:**
```sql
SELECT e.full_name, ea.hours_worked, ea.week_number
FROM employees e
JOIN employee_activities ea ON e.id = ea.employee_id
WHERE e.full_name IN ('Wei Zhang', 'Tao Huang') 
  AND ea.week_number = 1
ORDER BY e.full_name;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare the hours worked by '\''Wei Zhang'\'' and '\''Tao Huang'\'' during week 1."}'
```

---

## **Query 18: Who are the top 3 employees by total hours worked during the last 4 weeks?**

**SQL Query:**
```sql
SELECT e.full_name, SUM(ea.hours_worked) as total_hours
FROM employees e
JOIN employee_activities ea ON e.id = ea.employee_id
WHERE ea.week_number >= 7
GROUP BY e.full_name
ORDER BY total_hours DESC
LIMIT 3;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who are the top 3 employees by total hours worked during the last 4 weeks?"}'
```

---

## **Query 19: Who achieved the highest sales revenue in a single week, and when?**

**SQL Query:**
```sql
SELECT e.full_name, ea.total_sales, ea.week_number, cw.start_date, cw.end_date
FROM employees e
JOIN employee_activities ea ON e.id = ea.employee_id
JOIN calendar_weeks cw ON ea.week_number = cw.week_number
WHERE ea.total_sales IS NOT NULL
ORDER BY ea.total_sales DESC
LIMIT 1;
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who achieved the highest sales revenue in a single week, and when?"}'
```

---

## **Query 20: What is the total number of hours worked and average sales revenue for employees in the Business Development department?**

**SQL Query:**
```sql
SELECT 
    SUM(ea.hours_worked) as total_hours_worked,
    AVG(ea.total_sales) as average_sales_revenue,
    COUNT(DISTINCT e.id) as employee_count
FROM employees e
JOIN employee_activities ea ON e.id = ea.employee_id
WHERE e.department = 'Business Development';
```

**Command to Run:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the total number of hours worked and average sales revenue for employees in the Business Development department?"}'
```

---

## **Batch Command to Run All 20 Queries**

You can also run all queries at once using the benchmark endpoint:

```bash
curl -X POST "http://localhost:8000/api/v1/benchmark" \
  -H "Content-Type: application/json"
```

This will execute all 20 queries and return comprehensive results with execution times and success rates.

---

## **Direct Database Queries (Alternative)**

If you want to run the SQL directly against the database:

```bash
# Connect to PostgreSQL
psql -h localhost -U user -d employee_tracker

# Then run any of the SQL queries above directly
```

**Note:** Make sure your FastAPI server is running on `http://localhost:8000` before executing the curl commands. 