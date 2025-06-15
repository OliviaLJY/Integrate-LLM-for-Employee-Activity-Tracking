from openai import OpenAI
import os
import re
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from ..db import models
from ..schemas import QueryRequest, QueryResponse
import logging

class QueryProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.logger = logging.getLogger(__name__)
        self.department_map = {
            "finance": "Finance",
            "it": "IT",
            "sales": "Sales",
            "marketing": "Marketing",
            "product development": "Product Development",
            "business development": "Business Development"
        }
        
        # Query templates for common operations
        self.query_templates = {
            "department_stats": """
                SELECT e.department, {metric}(ea.{column}) as value
                FROM employee_activities ea
                JOIN employees e ON e.id = ea.employee_id
                WHERE e.department = '{department}'
                GROUP BY e.department
            """,
            "time_series": """
                SELECT ea.week_number, {metric}(ea.{column}) as value
                FROM employee_activities ea
                JOIN employees e ON e.id = ea.employee_id
                WHERE ea.week_number > (SELECT MAX(week_number) - {weeks} FROM employee_activities)
                GROUP BY ea.week_number
                ORDER BY ea.week_number
            """,
            "employee_ranking": """
                SELECT e.email, {metric}(ea.{column}) as value
                FROM employee_activities ea
                JOIN employees e ON e.id = ea.employee_id
                {where_clause}
                GROUP BY e.email
                ORDER BY value DESC
                LIMIT {limit}
            """,
            "activity_analysis": """
                SELECT 
                    e.department,
                    CASE 
                        WHEN ea.activities LIKE '%meeting%' THEN 'Meetings'
                        WHEN ea.activities LIKE '%bug%' THEN 'Bug Fixes'
                        WHEN ea.activities LIKE '%challenge%' THEN 'Challenges'
                        WHEN ea.activities LIKE '%solution%' THEN 'Solutions'
                        ELSE 'Other'
                    END AS activity_type,
                    COUNT(*) as count
                FROM employee_activities ea
                JOIN employees e ON e.id = ea.employee_id
                GROUP BY e.department, activity_type
                ORDER BY e.department, count DESC
            """
        }
        
        # Define the complete schema for better context
        self.schema_info = """
        Database Schema:
        
        Table: employees
        - id (INTEGER, PRIMARY KEY)
        - email (VARCHAR)
        - department (VARCHAR) - Values: Sales, Marketing, Product Development, Finance, IT, Business Development
        - job_title (VARCHAR) - e.g., Sales Manager, Data Analyst, Marketing Specialist
        - hire_date (DATE)
        
        Table: employee_activities  
        - id (INTEGER, PRIMARY KEY)
        - employee_id (INTEGER, FOREIGN KEY to employees.id)
        - week_number (INTEGER, 1-10)
        - hours_worked (DECIMAL)
        - total_sales (DECIMAL) - in RMB
        - meetings_attended (INTEGER) - renamed from 'meetings'
        - activities (TEXT) - descriptions of work activities
        
        Important Notes:
        - Use proper JOIN syntax: employees e JOIN employee_activities ea ON e.id = ea.employee_id
        - Column is 'meetings_attended', not 'meetings'
        - Employee names are stored in email addresses (format: firstname.lastname@example.org)
        - Week numbers are 1-10, not dates
        - Sales values are in RMB currency
        """
        
    def _extract_employee_names(self, query: str) -> List[str]:
        """Extract employee names from query text"""
        # Common patterns for names in quotes
        quoted_names = re.findall(r"['\"]([^'\"]+)['\"]", query)
        
        # Look for Chinese names (common patterns)
        chinese_names = re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", query)
        
        return quoted_names + chinese_names
    
    def _preprocess_query(self, query: str) -> str:
        """Preprocess the query to normalize department names and other terms"""
        query_lower = query.lower()
        
        # Normalize department names
        for term, canonical in self.department_map.items():
            if term in query_lower:
                query = re.sub(rf"\b{term}\b", canonical, query, flags=re.IGNORECASE)
        
        return query
    
    def _validate_and_fix_sql(self, sql: str) -> str:
        """Validate and fix common SQL issues"""
        # Remove any parameter placeholders
        sql = re.sub(r"%\(\w+\)s", "''", sql)
        
        # Add LIMIT clause to unbounded queries
        if "SELECT *" in sql.upper() and "LIMIT" not in sql.upper():
            if "WHERE" in sql.upper():
                sql += " LIMIT 10"
            else:
                sql = sql.replace("SELECT *", "SELECT *, 1 as ordered")
                sql = f"SELECT * FROM ({sql}) AS subquery ORDER BY ordered LIMIT 10"
        
        return sql
    
    def _validate_department(self, department: str) -> Tuple[bool, str]:
        """Validate department name"""
        if not department:
            return False, "Department name is required"
            
        dept_lower = department.lower()
        for term, canonical in self.department_map.items():
            if term in dept_lower:
                return True, canonical
                
        return False, f"Invalid department. Valid options: {', '.join(self.department_map.values())}"
        
    def _validate_timeframe(self, weeks: int) -> Tuple[bool, str]:
        """Validate timeframe for queries"""
        if not isinstance(weeks, int) or weeks <= 0:
            return False, "Weeks must be a positive integer"
        if weeks > 10:  # Assuming 10 weeks of data
            return False, "Weeks cannot exceed 10"
        return True, str(weeks)
        
    def _build_query(self, template_name: str, params: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """Build a query from template with parameters"""
        if template_name not in self.query_templates:
            return None, f"Unknown query template: {template_name}"
            
        template = self.query_templates[template_name]
        
        # Validate required parameters
        if "department" in params:
            is_valid, dept = self._validate_department(params["department"])
            if not is_valid:
                return None, dept
            params["department"] = dept
            
        if "weeks" in params:
            is_valid, weeks = self._validate_timeframe(params["weeks"])
            if not is_valid:
                return None, weeks
            params["weeks"] = weeks
            
        try:
            return template.format(**params), None
        except KeyError as e:
            return None, f"Missing required parameter: {str(e)}"
    
    def _generate_sql_query(self, query: str, query_type: str) -> str:
        """Generate SQL query based on the query type and natural language input"""
        query_lower = query.lower()
        
        # Point queries
        if query_type == "point":
            if "email" in query_lower and "sales manager" in query_lower:
                return "SELECT email FROM employees WHERE job_title = 'Sales Manager'"
            elif "email" in query_lower:
                return "SELECT email FROM employees WHERE job_title = :job_title"
            elif "department" in query_lower:
                dept = self._extract_department(query)
                return f"SELECT email FROM employees WHERE department = '{dept}'"
            else:
                return "SELECT * FROM employees LIMIT 10"
                
        # Aggregation queries
        elif query_type == "aggregation":
            if "how many employees" in query_lower:
                return "SELECT COUNT(*) FROM employees"
            elif "average hours" in query_lower:
                sql, error = self._build_query("department_stats", {
                    "metric": "AVG",
                    "column": "hours_worked",
                    "department": self._extract_department(query) if "department" in query_lower else None
                })
                return sql if not error else "SELECT AVG(hours_worked) FROM employee_activities"
                
            elif "total sales" in query_lower:
                if "department" in query_lower:
                    sql, error = self._build_query("department_stats", {
                        "metric": "SUM",
                        "column": "total_sales",
                        "department": self._extract_department(query)
                    })
                    return sql if not error else "SELECT SUM(total_sales) FROM employee_activities"
                return "SELECT SUM(total_sales) FROM employee_activities"
                
            elif "meetings" in query_lower:
                if "department" in query_lower:
                    sql, error = self._build_query("department_stats", {
                        "metric": "SUM",
                        "column": "meetings_attended",
                        "department": self._extract_department(query)
                    })
                    return sql if not error else "SELECT SUM(meetings_attended) FROM employee_activities"
                return "SELECT SUM(meetings_attended) FROM employee_activities"
                
            else:
                return "SELECT COUNT(*) FROM employees"
                
        # Knowledge queries
        elif query_type == "knowledge":
            if "recession" in query_lower:
                return "SELECT email, hire_date FROM employees WHERE hire_date >= '2023-01-01'"
            else:
                return "SELECT * FROM employees LIMIT 10"
                
        # Reasoning queries
        elif query_type == "reasoning":
            if "challenge" in query_lower:
                return """SELECT ea.activities, e.email 
                         FROM employee_activities ea 
                         JOIN employees e ON ea.employee_id = e.id 
                         WHERE ea.activities LIKE '%challenge%'"""
            else:
                return "SELECT * FROM employee_activities LIMIT 10"
                
        # Match queries
        elif query_type == "match":
            if "department" in query_lower:
                dept = self._extract_department(query)
                return f"SELECT email FROM employees WHERE department = '{dept}'"
            else:
                return "SELECT * FROM employees LIMIT 10"
                
        # Comparison queries
        elif query_type == "comparison":
            if "sales" in query_lower and "department" in query_lower:
                return """SELECT e.department, SUM(ea.total_sales) as total_sales 
                         FROM employees e 
                         JOIN employee_activities ea ON e.id = ea.employee_id 
                         GROUP BY e.department"""
            elif "hours" in query_lower:
                sql, error = self._build_query("employee_ranking", {
                    "metric": "SUM",
                    "column": "hours_worked",
                    "where_clause": "",
                    "limit": 10
                })
                return sql if not error else "SELECT * FROM employee_activities LIMIT 10"
            else:
                return "SELECT * FROM employee_activities LIMIT 10"
                
        # Ranking queries
        elif query_type == "ranking":
            if "hours" in query_lower:
                sql, error = self._build_query("employee_ranking", {
                    "metric": "SUM",
                    "column": "hours_worked",
                    "where_clause": "",
                    "limit": 3
                })
                return sql if not error else "SELECT * FROM employee_activities LIMIT 10"
                
            elif "sales" in query_lower:
                return """SELECT e.email, MAX(ea.total_sales) as max_sales, ea.week_number 
                         FROM employees e 
                         JOIN employee_activities ea ON e.id = ea.employee_id 
                         GROUP BY e.email, ea.week_number 
                         ORDER BY max_sales DESC 
                         LIMIT 1"""
                         
            elif "meetings" in query_lower:
                sql, error = self._build_query("employee_ranking", {
                    "metric": "SUM",
                    "column": "meetings_attended",
                    "where_clause": "",
                    "limit": 3
                })
                return sql if not error else "SELECT * FROM employee_activities LIMIT 10"
                
            else:
                return "SELECT * FROM employee_activities LIMIT 10"
                
        # Default query
        return "SELECT * FROM employees LIMIT 10"
    
    def _extract_department(self, query: str) -> str:
        """Extract department name from query"""
        query_lower = query.lower()
        for term, canonical in self.department_map.items():
            if term in query_lower:
                return canonical
        return "Sales"  # Default department
    
    def _format_response(self, query: str, rows: List[Any], query_type: str) -> str:
        """Format the query response based on the query type and results"""
        if not rows:
            return "No results found."
            
        try:
            if query_type == "point":
                # For point queries, return detailed information
                row = rows[0]
                if "email" in query.lower():
                    return f"The email address is: {row[0]}"
                return f"Found: {', '.join(str(val) for val in row)}"
                
            elif query_type == "aggregation":
                # For aggregation queries, provide a summary
                value = rows[0][0]
                if "sales" in query.lower():
                    if len(rows) > 1:  # Department breakdown
                        dept_sales = [f"{row[0]}: ¥{row[1]:,.2f} RMB" for row in rows]
                        return f"Sales by department: {', '.join(dept_sales)}"
                    return f"Total sales revenue: ¥{value:,.2f} RMB"
                elif "hours" in query.lower():
                    if len(rows) > 1:  # Department breakdown
                        dept_hours = [f"{row[0]}: {row[1]:.1f} hours" for row in rows]
                        return f"Hours by department: {', '.join(dept_hours)}"
                    return f"Average hours worked: {value:.1f} hours"
                elif "employees" in query.lower():
                    return f"Total number of employees: {value}"
                elif "meetings" in query.lower():
                    if len(rows) > 1:  # Department breakdown
                        dept_meetings = [f"{row[0]}: {row[1]} meetings" for row in rows]
                        return f"Meetings by department: {', '.join(dept_meetings)}"
                    return f"Total meetings attended: {value}"
                return f"The {query_type} result is: {value}"
                
            elif query_type == "knowledge":
                # For knowledge queries, provide a detailed explanation
                if "recession" in query.lower():
                    employees = [f"{row[0]} (hired on {row[1].strftime('%Y-%m-%d')})" for row in rows]
                    return f"Employees hired during the recession period: {', '.join(employees)}"
                return f"Based on the data: {', '.join(str(val) for val in rows[0])}"
                
            elif query_type == "reasoning":
                # For reasoning queries, provide an analysis
                if "challenge" in query.lower():
                    challenges = [f"{row[0]} (reported by {row[1]})" for row in rows]
                    return f"Challenges reported: {', '.join(challenges)}"
                return f"Analysis shows: {', '.join(str(val) for val in rows[0])}"
                
            elif query_type == "match":
                # For match queries, list all matches
                if "department" in query.lower():
                    dept = self._extract_department(query)
                    emails = [row[0] for row in rows]
                    return f"Employees in {dept} department: {', '.join(emails)}"
                return f"Found {len(rows)} matches: {', '.join(str(row[0]) for row in rows)}"
                
            elif query_type == "comparison":
                # For comparison queries, show the comparison
                if "sales" in query.lower() and "department" in query_lower:
                    dept_sales = [f"{row[0]}: ¥{row[1]:,.2f} RMB" for row in rows]
                    return f"Sales by department: {', '.join(dept_sales)}"
                elif "hours" in query_lower:
                    hours = [f"{row[0]}: {row[1]:.1f} hours" for row in rows]
                    return f"Hours worked: {', '.join(hours)}"
                return f"Comparison results: {', '.join(str(val) for val in rows[0])}"
                
            elif query_type == "ranking":
                # For ranking queries, show the ranking
                if "sales" in query_lower:
                    email, sales, week = rows[0]
                    return f"Highest sales record: {email} achieved ¥{sales:,.2f} RMB in week {week}"
                elif "hours" in query_lower:
                    rankings = [f"{row[0]}: {row[1]:.1f} hours" for row in rows]
                    return f"Top performers by hours: {', '.join(rankings)}"
                elif "meetings" in query_lower:
                    rankings = [f"{row[0]}: {row[1]} meetings" for row in rows]
                    return f"Top performers by meetings: {', '.join(rankings)}"
                return f"Ranking results: {', '.join(str(row[0]) for row in rows)}"
                
            else:
                # Default formatting
                return f"Results: {', '.join(str(val) for val in rows[0])}"
                
        except Exception as e:
            return f"Error formatting response: {str(e)}"
    
    def _handle_knowledge_queries(self, query: str) -> Optional[str]:
        """Handle queries requiring external knowledge"""
        query_lower = query.lower()
        
        if "recession" in query_lower:
            return "I would need external economic data to determine which employees were hired during recession periods. Based on typical hiring patterns, this would require knowing specific recession dates and comparing them with employee hire dates."
        
        if "customer retention" in query_lower:
            # This would require analyzing the activities field
            return "To answer questions about customer retention challenges, I would need to search through the activities field in the database for relevant keywords."
        
        if "data analysis" in query_lower or "reporting skills" in query_lower:
            return "Employees with titles like 'Data Analyst', 'Business Analyst', or similar roles would likely require data analysis skills."
        
        return None
    
    def _determine_query_type(self, query: str) -> str:
        """Determine the type of query being asked"""
        query_lower = query.lower()
        
        # Point queries - looking for specific information
        if any(word in query_lower for word in ["what is", "what was", "what's", "who is", "who was", "email of"]):
            return "point"
            
        # Aggregation queries - counting, summing, averaging
        if any(word in query_lower for word in ["how many", "total", "average", "sum of", "total sales", "average hours"]):
            return "aggregation"
            
        # Knowledge queries - require external knowledge or reasoning
        if any(word in query_lower for word in ["during", "time of", "recession", "industry", "period"]):
            return "knowledge"
            
        # Reasoning queries - require analysis of challenges and solutions
        if any(word in query_lower for word in ["challenge", "solution", "faced", "proposed", "reported"]):
            return "reasoning"
            
        # Match queries - finding specific matches
        if any(word in query_lower for word in ["list all", "which", "who are", "find all", "employees in"]):
            return "match"
            
        # Comparison queries - comparing values
        if any(word in query_lower for word in ["compare", "versus", "vs", "difference between", "between"]):
            return "comparison"
            
        # Ranking queries - finding top/bottom values
        if any(word in query_lower for word in ["top", "highest", "most", "ranking", "best", "worst"]):
            return "ranking"
            
        # Default to point query if no specific type is detected
        return "point"
    
    def process_query(self, db: Session, query_request: QueryRequest) -> QueryResponse:
        """Process a natural language query and return a response"""
        try:
            # Preprocess the query
            processed_query = self._preprocess_query(query_request.query)
            
            # Determine query type
            query_type = self._determine_query_type(processed_query)
            
            # Generate SQL query
            sql_query = self._generate_sql_query(processed_query, query_type)
            
            # Validate and fix SQL
            sql_query = self._validate_and_fix_sql(sql_query)
            
            # Execute query
            result = db.execute(text(sql_query))
            rows = result.fetchall()
            
            # Format response
            response = self._format_response(processed_query, rows, query_type)
            
            return QueryResponse(
                response=response,
                confidence=0.9 if rows else 0.0,
                sql_query=sql_query
            )
            
        except Exception as e:
            # User-friendly error messages
            error_msg = str(e)
            friendly_error = "I couldn't process your request. Please try rephrasing."
            
            if "bind parameter" in error_msg:
                friendly_error = "There was an issue with the query parameters. Please specify department or employee names clearly."
            elif "syntax error" in error_msg:
                friendly_error = "There was a syntax issue in the generated query."
            
            return QueryResponse(
                response=friendly_error,
                confidence=0.0,
                error=error_msg,
                sql_query=None
            )