# Direct PostgreSQL Commands for All 20 Queries

Connect to your database first:
```bash
psql -d employee_tracker -c "YOUR_QUERY_HERE"
```

Or connect interactively:
```bash
psql -d employee_tracker
```

---

## **Query 1: Sales Manager Email**
```bash
psql -d employee_tracker -c "SELECT email, full_name FROM employees WHERE job_title = 'Sales Manager';"
```

## **Query 2: Product Development Employees**
```bash
psql -d employee_tracker -c "SELECT full_name, job_title, email FROM employees WHERE department = 'Product Development';"
```

## **Query 3: Wei Zhang Sales Revenue for Week Starting 2024-08-28**
```bash
psql -d employee_tracker -c "SELECT e.full_name, ea.total_sales, cw.start_date, cw.end_date FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id JOIN calendar_weeks cw ON ea.week_number = cw.week_number WHERE e.full_name = 'Wei Zhang' AND cw.start_date <= '2024-08-28' AND cw.end_date >= '2024-08-28';"
```

## **Query 4: Finance Department Employees**
```bash
psql -d employee_tracker -c "SELECT full_name, job_title, email FROM employees WHERE department = 'Finance';"
```

## **Query 5: Na Li Total Meetings**
```bash
psql -d employee_tracker -c "SELECT e.full_name, SUM(ea.meetings_attended) as total_meetings FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id WHERE e.full_name = 'Na Li' GROUP BY e.full_name;"
```

## **Query 6: Employees Working >40 Hours in Week 1**
```bash
psql -d employee_tracker -c "SELECT e.full_name, ea.hours_worked FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id WHERE ea.week_number = 1 AND ea.hours_worked > 40 ORDER BY ea.hours_worked DESC;"
```

## **Query 7: Total Number of Employees**
```bash
psql -d employee_tracker -c "SELECT COUNT(*) as total_employees FROM employees;"
```

## **Query 8: Average Hours Worked in Week 2**
```bash
psql -d employee_tracker -c "SELECT AVG(hours_worked) as average_hours FROM employee_activities WHERE week_number = 2;"
```

## **Query 9: Total Sales Revenue by Sales Department**
```bash
psql -d employee_tracker -c "SELECT SUM(ea.total_sales) as total_sales_revenue FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id WHERE e.department = 'Sales' AND ea.total_sales IS NOT NULL;"
```

## **Query 10: Total Sales Revenue in Week 1**
```bash
psql -d employee_tracker -c "SELECT SUM(total_sales) as total_week1_sales FROM employee_activities WHERE week_number = 1 AND total_sales IS NOT NULL;"
```

## **Query 11: Most Hours Worked in First Week of September 2024**
```bash
psql -d employee_tracker -c "SELECT e.full_name, ea.hours_worked, cw.start_date FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id JOIN calendar_weeks cw ON ea.week_number = cw.week_number WHERE cw.start_date >= '2024-09-01' AND cw.start_date < '2024-09-08' ORDER BY ea.hours_worked DESC LIMIT 1;"
```

## **Query 12: Most Meetings Attended in Week 2**
```bash
psql -d employee_tracker -c "SELECT e.full_name, ea.meetings_attended FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id WHERE ea.week_number = 2 ORDER BY ea.meetings_attended DESC LIMIT 1;"
```

## **Query 13: Employees Hired During Recession (2023)**
```bash
psql -d employee_tracker -c "SELECT full_name, hire_date, department, job_title FROM employees WHERE hire_date >= '2023-01-01' AND hire_date <= '2023-12-31' ORDER BY hire_date;"
```

## **Query 14: Customer Retention Challenges**
```bash
psql -d employee_tracker -c "SELECT e.full_name, ea.activities, ea.week_number FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id WHERE ea.activities ILIKE '%customer retention%' OR ea.activities ILIKE '%retention%' ORDER BY e.full_name, ea.week_number;"
```

## **Query 15: Data Analysis/Reporting Roles**
```bash
psql -d employee_tracker -c "SELECT full_name, job_title, department FROM employees WHERE job_title ILIKE '%analyst%' OR job_title ILIKE '%data%' OR job_title ILIKE '%report%' OR job_title ILIKE '%financial%' ORDER BY department, full_name;"
```

## **Query 16: IT Department Employees**
```bash
psql -d employee_tracker -c "SELECT full_name, job_title, email, hire_date FROM employees WHERE department = 'IT' ORDER BY full_name;"
```

## **Query 17: Compare Wei Zhang vs Tao Huang Hours in Week 1**
```bash
psql -d employee_tracker -c "SELECT e.full_name, ea.hours_worked, ea.week_number FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id WHERE e.full_name IN ('Wei Zhang', 'Tao Huang') AND ea.week_number = 1 ORDER BY e.full_name;"
```

## **Query 18: Top 3 Employees by Hours in Last 4 Weeks**
```bash
psql -d employee_tracker -c "SELECT e.full_name, SUM(ea.hours_worked) as total_hours FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id WHERE ea.week_number >= 7 GROUP BY e.full_name ORDER BY total_hours DESC LIMIT 3;"
```

## **Query 19: Highest Sales Revenue in Single Week**
```bash
psql -d employee_tracker -c "SELECT e.full_name, ea.total_sales, ea.week_number, cw.start_date, cw.end_date FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id JOIN calendar_weeks cw ON ea.week_number = cw.week_number WHERE ea.total_sales IS NOT NULL ORDER BY ea.total_sales DESC LIMIT 1;"
```

## **Query 20: Business Development Department Stats**
```bash
psql -d employee_tracker -c "SELECT SUM(ea.hours_worked) as total_hours_worked, AVG(ea.total_sales) as average_sales_revenue, COUNT(DISTINCT e.id) as employee_count FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id WHERE e.department = 'Business Development';"
```

---

## **Bonus: Useful Database Exploration Commands**

### **Check All Tables**
```bash
psql -d employee_tracker -c "\dt"
```

### **View All Employees**
```bash
psql -d employee_tracker -c "SELECT * FROM employees ORDER BY department, full_name;"
```

### **View All Departments**
```bash
psql -d employee_tracker -c "SELECT DISTINCT department FROM employees ORDER BY department;"
```

### **View Calendar Weeks**
```bash
psql -d employee_tracker -c "SELECT * FROM calendar_weeks ORDER BY week_number;"
```

### **Sample Employee Activities**
```bash
psql -d employee_tracker -c "SELECT e.full_name, ea.week_number, ea.hours_worked, ea.total_sales, ea.meetings_attended FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id ORDER BY e.full_name, ea.week_number LIMIT 20;"
```

### **Department Summary**
```bash
psql -d employee_tracker -c "SELECT e.department, COUNT(*) as employee_count, AVG(ea.hours_worked) as avg_hours, SUM(ea.total_sales) as total_sales FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id GROUP BY e.department ORDER BY e.department;"
```

### **Weekly Summary**
```bash
psql -d employee_tracker -c "SELECT ea.week_number, COUNT(DISTINCT ea.employee_id) as active_employees, AVG(ea.hours_worked) as avg_hours, SUM(ea.total_sales) as total_sales FROM employee_activities ea GROUP BY ea.week_number ORDER BY ea.week_number;"
```

---

## **Quick Test Script**

Save this as `test_queries.sh`:

```bash
#!/bin/bash

echo "=== Testing All 20 Queries ==="

echo "Query 1: Sales Manager"
psql -d employee_tracker -c "SELECT email, full_name FROM employees WHERE job_title = 'Sales Manager';"

echo -e "\nQuery 2: Product Development"
psql -d employee_tracker -c "SELECT full_name, job_title FROM employees WHERE department = 'Product Development';"

echo -e "\nQuery 7: Total Employees"
psql -d employee_tracker -c "SELECT COUNT(*) as total_employees FROM employees;"

echo -e "\nQuery 13: Recession Hires"
psql -d employee_tracker -c "SELECT full_name, hire_date FROM employees WHERE hire_date >= '2023-01-01' AND hire_date <= '2023-12-31';"

echo -e "\nQuery 16: IT Department"
psql -d employee_tracker -c "SELECT full_name, job_title FROM employees WHERE department = 'IT';"

echo "=== Test Complete ==="
```

Make it executable and run:
```bash
chmod +x test_queries.sh
./test_queries.sh
``` 