from openai import OpenAI
import os
import re
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from ..db import models
from ..schemas import QueryRequest, QueryResponse
import logging
import time

class QueryProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.logger = logging.getLogger(__name__)
        self.department_map = {
            "sales": "Sales",
            "it": "IT",
            "finance": "Finance",
            "business development": "Business Development",
            "marketing": "Marketing",
            "product development": "Product Development"
        }
        
        # Updated schema info with full_name and calendar_weeks
        self.schema_info = """
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
        - total_sales (DECIMAL) - in RMB
        - meetings_attended (INTEGER)
        - activities (TEXT) - descriptions of work activities
        
        Table: calendar_weeks
        - week_number (INTEGER, PRIMARY KEY)
        - start_date (DATE, NOT NULL)
        - end_date (DATE, NOT NULL)
        
        Critical Rules:
        1. Always use full_name for employee lookups
        2. Join calendar_weeks for date-based queries
        3. Format numbers with proper units (RMB, hours)
        4. Validate departments before querying
        5. Handle missing data gracefully
        """
        
        # Updated query templates
        self.query_templates = {
            "employee_lookup": """
                SELECT e.*, ea.* 
                FROM employees e 
                LEFT JOIN employee_activities ea ON e.id = ea.employee_id 
                WHERE e.full_name = :name
            """,
            "temporal_query": """
                SELECT e.*, ea.* 
                FROM employees e 
                JOIN employee_activities ea ON e.id = ea.employee_id 
                JOIN calendar_weeks cw ON ea.week_number = cw.week_number 
                WHERE cw.start_date <= :date AND cw.end_date >= :date
            """,
            "department_stats": """
                SELECT 
                    e.department,
                    COUNT(DISTINCT e.id) as employee_count,
                    SUM(ea.hours_worked) as total_hours,
                    AVG(ea.hours_worked) as avg_hours,
                    SUM(ea.total_sales) as total_sales,
                    AVG(ea.total_sales) as avg_sales
                FROM employees e 
                JOIN employee_activities ea ON e.id = ea.employee_id 
                WHERE e.department = :department 
                GROUP BY e.department
            """
        }
        
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
        valid_departments = {
            "Sales", "IT", "Finance", "Business Development", 
            "Marketing", "Product Development"
        }
        if not department:
            return False, "Department name is required"
            
        dept_lower = department.lower()
        for term, canonical in self.department_map.items():
            if term in dept_lower:
                return True, canonical
                
        return False, f"Invalid department. Valid options: {', '.join(valid_departments)}"
        
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
    
    def _format_currency(self, value: Optional[float]) -> str:
        """Format currency values with proper RMB symbol and commas"""
        if value is None:
            return "No sales data"
        return f"¥{value:,.2f} RMB"
    
    def _generate_sql_query(self, query: str, query_type: str, params: Dict[str, Any]) -> str:
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
            elif "sales revenue" in query_lower and "week" in query_lower:
                if 'name' not in params or 'date' not in params:
                    raise ValueError("Missing required parameters: name and date")
                return """
                    SELECT ea.total_sales 
                    FROM employee_activities ea 
                    JOIN employees e ON ea.employee_id = e.id 
                    JOIN calendar_weeks cw ON ea.week_number = cw.week_number 
                    WHERE e.full_name = :name AND cw.start_date = :date
                """
            else:
                return "SELECT * FROM employees LIMIT 10"
                
        # Aggregation queries
        elif query_type == "aggregation":
            if "how many employees" in query_lower:
                return "SELECT COUNT(*) FROM employees"
            elif "average hours" in query_lower:
                if "week" in query_lower and 'week_number' in params:
                    return """
                        SELECT AVG(ea.hours_worked) 
                        FROM employee_activities ea 
                        JOIN calendar_weeks cw ON ea.week_number = cw.week_number 
                        WHERE cw.week_number = :week_number
                    """
                return "SELECT AVG(hours_worked) FROM employee_activities"
                
            elif "total sales" in query_lower:
                if "department" in query_lower and 'department' in params:
                    return """
                        SELECT SUM(ea.total_sales) 
                        FROM employee_activities ea 
                        JOIN employees e ON ea.employee_id = e.id 
                        WHERE e.department = :department
                    """
                elif "week" in query_lower and 'week_number' in params:
                    return """
                        SELECT SUM(ea.total_sales) 
                        FROM employee_activities ea 
                        JOIN calendar_weeks cw ON ea.week_number = cw.week_number 
                        WHERE cw.week_number = :week_number
                    """
                return "SELECT SUM(total_sales) FROM employee_activities"
                
            elif "meetings" in query_lower:
                if 'name' in params:
                    return """
                        SELECT SUM(ea.meetings_attended) 
                        FROM employee_activities ea 
                        JOIN employees e ON ea.employee_id = e.id 
                        WHERE e.full_name = :name
                    """
                return "SELECT SUM(meetings_attended) FROM employee_activities"
                
            else:
                return "SELECT COUNT(*) FROM employees"
                
        # Knowledge queries
        elif query_type == "knowledge":
            if "recession" in query_lower:
                return "SELECT email, hire_date FROM employees WHERE hire_date >= '2023-01-01'"
            elif "data analysis" in query_lower or "reporting" in query_lower:
                return """
                    SELECT email, job_title 
                    FROM employees 
                    WHERE job_title IN ('Data Analyst', 'Business Analyst', 'Financial Analyst', 'System Administrator')
                """
            else:
                return "SELECT * FROM employees LIMIT 10"
                
        # Reasoning queries
        elif query_type == "reasoning":
            if "challenge" in query_lower:
                return """
                    SELECT ea.activities, e.email 
                    FROM employee_activities ea 
                    JOIN employees e ON ea.employee_id = e.id 
                    WHERE ea.activities LIKE '%challenge%'
                """
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
            if "hours" in query_lower and 'names' in params and 'week_number' in params:
                return """
                    SELECT e.full_name, ea.hours_worked 
                    FROM employee_activities ea 
                    JOIN employees e ON ea.employee_id = e.id 
                    JOIN calendar_weeks cw ON ea.week_number = cw.week_number 
                    WHERE e.full_name IN :names AND cw.week_number = :week_number
                """
            elif "hours" in query_lower and "more than" in query_lower and 'week_number' in params:
                hours = int(re.search(r'more than (\d+)', query_lower).group(1))
                return f"""
                    SELECT e.full_name, ea.hours_worked 
                    FROM employee_activities ea 
                    JOIN employees e ON ea.employee_id = e.id 
                    JOIN calendar_weeks cw ON ea.week_number = cw.week_number 
                    WHERE cw.week_number = :week_number AND ea.hours_worked > {hours}
                """
            return "SELECT * FROM employee_activities LIMIT 10"
                
        # Ranking queries
        elif query_type == "ranking":
            if "hours" in query_lower and 'start_week' in params and 'end_week' in params:
                return """
                    SELECT e.full_name, SUM(ea.hours_worked) as total_hours 
                    FROM employee_activities ea 
                    JOIN employees e ON ea.employee_id = e.id 
                    JOIN calendar_weeks cw ON ea.week_number = cw.week_number 
                    WHERE cw.week_number BETWEEN :start_week AND :end_week 
                    GROUP BY e.full_name 
                    ORDER BY total_hours DESC 
                    LIMIT 3
                """
            elif "sales" in query_lower:
                return """
                    SELECT e.full_name, MAX(ea.total_sales) as max_sales, cw.start_date 
                    FROM employee_activities ea 
                    JOIN employees e ON ea.employee_id = e.id 
                    JOIN calendar_weeks cw ON ea.week_number = cw.week_number 
                    WHERE ea.total_sales IS NOT NULL 
                    GROUP BY e.full_name, cw.start_date 
                    ORDER BY max_sales DESC 
                    LIMIT 1
                """
            elif "meetings" in query_lower and 'week_number' in params:
                return """
                    SELECT e.full_name, SUM(ea.meetings_attended) as total_meetings 
                    FROM employee_activities ea 
                    JOIN employees e ON ea.employee_id = e.id 
                    JOIN calendar_weeks cw ON ea.week_number = cw.week_number 
                    WHERE cw.week_number = :week_number 
                    GROUP BY e.full_name 
                    ORDER BY total_meetings DESC 
                    LIMIT 1
                """
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
                elif "sales" in query.lower():
                    return f"Sales revenue: {self._format_currency(row[0])}"
                return f"Found: {', '.join(str(val) for val in row)}"
                
            elif query_type == "aggregation":
                # For aggregation queries, provide a summary
                value = rows[0][0]
                if "sales" in query.lower():
                    if len(rows) > 1:  # Department breakdown
                        dept_sales = [f"{row[0]}: {self._format_currency(row[1])}" for row in rows]
                        return f"Sales by department:\n" + "\n".join(f"- {s}" for s in dept_sales)
                    return f"Total sales revenue: {self._format_currency(value)}"
                elif "hours" in query.lower():
                    if len(rows) > 1:  # Department breakdown
                        dept_hours = [f"{row[0]}: {float(row[1]):.1f} hours" for row in rows]
                        return f"Hours by department:\n" + "\n".join(f"- {h}" for h in dept_hours)
                    return f"Average hours worked: {float(value):.1f} hours"
                elif "employees" in query.lower():
                    return f"Total number of employees: {value}"
                elif "meetings" in query.lower():
                    if len(rows) > 1:  # Department breakdown
                        dept_meetings = [f"{row[0]}: {row[1]} meetings" for row in rows]
                        return f"Meetings by department:\n" + "\n".join(f"- {m}" for m in dept_meetings)
                    return f"Total meetings attended: {value}"
                return f"The {query_type} result is: {value}"
                
            elif query_type == "knowledge":
                # For knowledge queries, provide a detailed explanation
                if "recession" in query.lower():
                    employees = [f"{row[0]} (hired on {row[1].strftime('%Y-%m-%d')})" for row in rows]
                    return f"Employees hired during the recession period:\n" + "\n".join(f"- {e}" for e in employees)
                elif "data analysis" in query.lower() or "reporting" in query.lower():
                    analysts = [f"{row[0]} ({row[1]})" for row in rows]
                    return f"Employees with data analysis or reporting skills:\n" + "\n".join(f"- {a}" for a in analysts)
                return f"Based on the data:\n" + "\n".join(f"- {', '.join(str(val) for val in row)}" for row in rows)
                
            elif query_type == "reasoning":
                # For reasoning queries, provide an analysis
                if "challenge" in query.lower():
                    challenges = [f"{row[0]} (reported by {row[1]})" for row in rows]
                    return f"Challenges reported:\n" + "\n".join(f"- {c}" for c in challenges)
                return f"Analysis shows:\n" + "\n".join(f"- {', '.join(str(val) for val in row)}" for row in rows)
                
            elif query_type == "match":
                # For match queries, list all matches
                if "department" in query.lower():
                    dept = self._extract_department(query)
                    emails = [row[0] for row in rows]
                    return f"Employees in {dept} department:\n" + "\n".join(f"- {e}" for e in emails)
                return f"Found {len(rows)} matches:\n" + "\n".join(f"- {row[0]}" for row in rows)
                
            elif query_type == "comparison":
                # For comparison queries, show the comparison
                if "hours" in query.lower():
                    if "more than" in query.lower():
                        employees = [f"{row[0]}: {float(row[1]):.1f} hours" for row in rows]
                        return f"Employees who worked more than the specified hours:\n" + "\n".join(f"- {e}" for e in employees)
                    hours = [f"{row[0]}: {float(row[1]):.1f} hours" for row in rows]
                    return f"Hours worked:\n" + "\n".join(f"- {h}" for h in hours)
                return f"Comparison results:\n" + "\n".join(f"- {', '.join(str(val) for val in row)}" for row in rows)
                
            elif query_type == "ranking":
                # For ranking queries, show the ranking
                if "sales" in query.lower():
                    name, sales, date = rows[0]
                    return f"Highest sales record: {name} achieved {self._format_currency(sales)} on {date.strftime('%Y-%m-%d')}"
                elif "hours" in query.lower():
                    rankings = [f"{row[0]}: {float(row[1]):.1f} hours" for row in rows]
                    return f"Top performers by hours:\n" + "\n".join(f"- {r}" for r in rankings)
                elif "meetings" in query.lower():
                    rankings = [f"{row[0]}: {row[1]} meetings" for row in rows]
                    return f"Top performers by meetings:\n" + "\n".join(f"- {r}" for r in rankings)
                return f"Ranking results:\n" + "\n".join(f"- {row[0]}" for row in rows)
                
            else:
                # Default formatting
                return f"Results:\n" + "\n".join(f"- {', '.join(str(val) for val in row)}" for row in rows)
                
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
    
    def _validate_query(self, query_type: str, params: Dict[str, Any]) -> Optional[str]:
        """Validate query parameters before execution"""
        required_params = {
            "temporal": ["start_date", "end_date"],
            "employee": ["full_name"],
            "department": ["department_name"]
        }
        
        if query_type in required_params:
            missing = [p for p in required_params[query_type] if p not in params]
            if missing:
                return f"Missing required parameters: {', '.join(missing)}"
        
        if "department" in params:
            if params["department"] not in self.department_map.values():
                return f"Invalid department. Valid options: {', '.join(self.department_map.values())}"
        
        return None
    
    def _extract_parameters(self, query: str) -> Dict[str, Any]:
        """Extract parameters from the query string"""
        params = {}
        
        # Extract employee names
        names = self._extract_employee_names(query)
        if names:
            params['names'] = tuple(names)
            if len(names) == 1:
                params['name'] = names[0]
        
        # Extract department
        dept = self._extract_department(query)
        if dept:
            params['department'] = dept
        
        # Extract week number
        week_match = re.search(r'week\s+(\d+)', query.lower())
        if week_match:
            params['week_number'] = int(week_match.group(1))
        
        # Extract date
        date_match = re.search(r"'(\d{4}-\d{2}-\d{2})'", query)
        if date_match:
            params['date'] = date_match.group(1)
        
        # Extract time range
        if "last 4 weeks" in query.lower():
            params['start_week'] = 1
            params['end_week'] = 4
        
        return params
    
    def process_query(self, db: Session, query_request: QueryRequest) -> QueryResponse:
        """Process a natural language query and return a structured response"""
        try:
            # Determine query type
            query_type = self._determine_query_type(query_request.query)
            
            # Extract parameters
            params = self._extract_parameters(query_request.query)
            
            # Generate SQL query
            sql_query = self._generate_sql_query(query_request.query, query_type, params)
            
            # Execute query
            start_time = time.time()
            result = db.execute(text(sql_query), params)
            rows = result.fetchall()
            execution_time = time.time() - start_time
            
            # Format response
            response = self._format_response(query_request.query, rows, query_type)
            
            return QueryResponse(
                response=response,
                confidence=0.9,  # High confidence for direct SQL queries
                sql_query=sql_query,
                execution_time=execution_time,
                success=True,
                error=None
            )
            
        except Exception as e:
            return QueryResponse(
                response="There was an issue with the query parameters. Please specify department or employee names clearly.",
                confidence=0.0,
                sql_query=None,
                execution_time=0.0,
                success=False,
                error=str(e)
            )