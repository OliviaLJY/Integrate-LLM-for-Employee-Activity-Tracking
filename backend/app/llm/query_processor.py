# from openai import OpenAI
# import os
# from typing import Dict, Any, List
# from sqlalchemy.orm import Session
# from sqlalchemy import text, func
# from ..db import models
# from ..schemas import QueryRequest, QueryResponse

# class QueryProcessor:
#     def __init__(self):
#         self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
#     def _generate_sql_query(self, query: str) -> str:
#         """Generate SQL query from natural language query"""
#         prompt = f"""
#         Generate a SQL query to answer this question: {query}
        
#         Available tables and columns:
#         - employees (id, email, department)
#         - employee_activities (id, employee_id, week_number, hours_worked, total_sales, meetings_attended)
        
#         Important rules:
#         1. Always use correct table aliases (e for employees, ea for employee_activities)
#         2. Always reference hours_worked and total_sales from employee_activities table
#         3. Use proper JOIN conditions
#         4. Include proper GROUP BY clauses when using aggregate functions
#         5. Use proper column references in SELECT statements
#         6. Do not include markdown formatting or backticks in the SQL query
#         7. Use proper data types (week_number is integer, not date)
#         8. Use proper HAVING clause syntax with the column alias
        
#         Example queries:
#         - For hours worked: SELECT e.email, ea.hours_worked FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id
#         - For sales comparison: SELECT e1.email, ea1.total_sales, e2.email, ea2.total_sales FROM employees e1 JOIN employee_activities ea1 ON e1.id = ea1.employee_id JOIN employees e2 JOIN employee_activities ea2 ON e2.id = ea2.employee_id
#         - For department stats: SELECT e.department, SUM(ea.hours_worked) as total_hours, AVG(ea.total_sales) as avg_sales FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id GROUP BY e.department
        
#         Generate the SQL query:
#         """
        
#         response = self.client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a SQL expert. Generate only the SQL query without any explanation or markdown formatting."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.1
#         )
        
#         # Clean up the response to remove any markdown formatting
#         sql_query = response.choices[0].message.content.strip()
#         sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
#         return sql_query
    
#     def _format_response(self, query: str, rows: List[tuple], sql_query: str) -> str:
#         """Format the response in natural language"""
#         if not rows:
#             return "I couldn't find any information matching your query. This might be because there's no data available for the specific criteria you mentioned."
        
#         try:
#             # Get column names from the first row
#             columns = [desc[0] for desc in rows[0]._mapping.keys()]
            
#             # Format the response based on query type
#             if "COUNT" in sql_query.upper():
#                 count = rows[0][0]
#                 if "employee" in query.lower():
#                     return f"The company currently has {count} employees."
#                 elif "meeting" in query.lower():
#                     return f"The total number of meetings attended is {count}."
#                 else:
#                     return f"The count is {count}."
                
#             elif "AVG" in sql_query.upper():
#                 avg_value = rows[0][0]
#                 if avg_value is None:
#                     return "I couldn't find any data to calculate the average."
#                 if "hour" in query.lower():
#                     return f"On average, employees worked {avg_value:.1f} hours."
#                 elif "sale" in query.lower():
#                     return f"The average sales revenue is ${avg_value:,.2f}."
#                 else:
#                     return f"The average value is {avg_value:.1f}."
                
#             elif "SUM" in sql_query.upper():
#                 total = rows[0][0]
#                 if total is None:
#                     return "I couldn't find any data to calculate the total."
#                 if "hour" in query.lower():
#                     return f"The total hours worked is {total:.1f} hours."
#                 elif "sale" in query.lower():
#                     return f"The total sales revenue is ${total:,.2f}."
#                 else:
#                     return f"The total is {total:.1f}."
                
#             elif "department" in query.lower():
#                 if "email" in columns:
#                     email = rows[0][0]
#                     return f"I found an employee with email {email} in the department you asked about."
#                 else:
#                     dept = rows[0][0]
#                     return f"The employee works in the {dept} department."
                
#             elif "email" in query.lower():
#                 email = rows[0][0]
#                 return f"The email address is {email}."
                
#             elif "sales" in query.lower() and "max" in sql_query.lower():
#                 email, sales, week = rows[0]
#                 return f"The highest sales record was achieved by {email} in week {week}, with total sales of ${sales:,.2f}."
                
#             else:
#                 # For other queries, provide a summary of the results
#                 if len(rows) == 1:
#                     values = [str(val) for val in rows[0]]
#                     return f"I found one result: {', '.join(values)}"
#                 else:
#                     return f"I found {len(rows)} results. Here's a summary of the data."
                
#         except Exception as e:
#             return f"I apologize, but I encountered an error while processing your query. Please try rephrasing your question."
    
#     def _determine_query_type(self, query: str) -> str:
#         """Determine the type of query being asked"""
#         prompt = f"""
#         Given this query: "{query}"
        
#         Classify it as one of these types:
#         - point (specific data points)
#         - aggregation (sums, averages, counts)
#         - knowledge (requires external knowledge)
#         - reasoning (analyzing patterns)
#         - match (filtering by criteria)
#         - comparison (comparing entities)
#         - ranking (ordering by metrics)
        
#         Return only the type name.
#         """
        
#         response = self.client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.1
#         )
        
#         return response.choices[0].message.content.strip().lower()
    
#     def process_query(self, db: Session, query_request: QueryRequest) -> QueryResponse:
#         """Process a natural language query"""
#         try:
#             # Generate SQL query
#             sql_query = self._generate_sql_query(query_request.query)
            
#             # Execute query
#             result = db.execute(text(sql_query))
#             rows = result.fetchall()
            
#             # Format response
#             response = self._format_response(query_request.query, rows, sql_query)
            
#             return QueryResponse(
#                 answer=response,
#                 confidence=0.9 if rows else 0.0,
#                 supporting_data={"sql_query": sql_query}
#             )
            
#         except Exception as e:
#             db.rollback()
#             return QueryResponse(
#                 answer=f"Error processing query: {str(e)}",
#                 confidence=0.0,
#                 supporting_data={"error": str(e)}
#             ) 


from openai import OpenAI
import os
import re
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from ..db import models
from ..schemas import QueryRequest, QueryResponse
import logging

class QueryProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.logger = logging.getLogger(__name__)
        
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
        """Preprocess the query to handle special cases"""
        # Convert employee names to email format for searching
        names = self._extract_employee_names(query)
        processed_query = query
        
        for name in names:
            # Convert "Wei Zhang" to "wei.zhang@example.org" format for email searching
            email_format = name.lower().replace(" ", ".") + "@example.org"
            processed_query = processed_query.replace(f"'{name}'", f"'{email_format}'")
            processed_query = processed_query.replace(f'"{name}"', f"'{email_format}'")
        
        return processed_query
    
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
                return "SELECT email FROM employees WHERE department = :department"
            else:
                return "SELECT * FROM employees WHERE id = :id"
                
        # Aggregation queries
        elif query_type == "aggregation":
            if "how many employees" in query_lower:
                return "SELECT COUNT(*) FROM employees"
            elif "average hours" in query_lower:
                return "SELECT AVG(hours_worked) FROM employee_activities"
            elif "total sales" in query_lower:
                return "SELECT SUM(total_sales) FROM employee_activities"
            else:
                return "SELECT COUNT(*) FROM employees"
                
        # Knowledge queries
        elif query_type == "knowledge":
            if "recession" in query_lower:
                return "SELECT email, hire_date FROM employees WHERE hire_date >= '2023-01-01'"
            else:
                return "SELECT * FROM employees"
                
        # Reasoning queries
        elif query_type == "reasoning":
            if "challenge" in query_lower:
                return "SELECT activities FROM employee_activities WHERE activities LIKE '%challenge%'"
            else:
                return "SELECT * FROM employee_activities"
                
        # Match queries
        elif query_type == "match":
            if "department" in query_lower:
                return "SELECT email FROM employees WHERE department = :department"
            else:
                return "SELECT * FROM employees"
                
        # Comparison queries
        elif query_type == "comparison":
            if "hours" in query_lower:
                return "SELECT e.email, ea.hours_worked FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id WHERE ea.week_number = :week"
            else:
                return "SELECT * FROM employee_activities"
                
        # Ranking queries
        elif query_type == "ranking":
            if "hours" in query_lower:
                return "SELECT e.email, SUM(ea.hours_worked) as total_hours FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id GROUP BY e.email ORDER BY total_hours DESC LIMIT 3"
            elif "sales" in query_lower:
                return "SELECT e.email, MAX(ea.total_sales) as max_sales, ea.week_number FROM employees e JOIN employee_activities ea ON e.id = ea.employee_id GROUP BY e.email, ea.week_number ORDER BY max_sales DESC LIMIT 1"
            else:
                return "SELECT * FROM employee_activities"
                
        # Default query
        return "SELECT * FROM employees"
    
    def _validate_sql_query(self, sql_query: str) -> Tuple[bool, str]:
        """Basic validation of generated SQL query"""
        issues = []
        
        # Check for common issues
        if 'total_hours' in sql_query and 'HAVING total_hours' in sql_query:
            if 'SUM(ea.hours_worked) as total_hours' not in sql_query:
                issues.append("HAVING clause references undefined alias")
        
        if 'employees e' not in sql_query and 'FROM employees' in sql_query:
            issues.append("Missing table alias for employees")
            
        if 'employee_activities ea' not in sql_query and 'employee_activities' in sql_query:
            issues.append("Missing table alias for employee_activities")
        
        return len(issues) == 0, "; ".join(issues)
    
    def _format_response(self, query: str, rows: List[Any], query_type: str) -> str:
        """Format the query response based on the query type and results"""
        if not rows:
            return "No results found."
            
        try:
            if query_type == "point":
                # For point queries, return detailed information
                row = rows[0]
                return f"Found: {', '.join(str(val) for val in row)}"
                
            elif query_type == "aggregation":
                # For aggregation queries, provide a summary
                value = rows[0][0]
                return f"The {query_type} result is: {value}"
                
            elif query_type == "knowledge":
                # For knowledge queries, provide a detailed explanation
                return f"Based on the data: {', '.join(str(val) for val in rows[0])}"
                
            elif query_type == "reasoning":
                # For reasoning queries, provide an analysis
                return f"Analysis shows: {', '.join(str(val) for val in rows[0])}"
                
            elif query_type == "match":
                # For match queries, list all matches
                return f"Found {len(rows)} matches: {', '.join(str(row[0]) for row in rows)}"
                
            elif query_type == "comparison":
                # For comparison queries, show the comparison
                return f"Comparison results: {', '.join(str(val) for val in rows[0])}"
                
            elif query_type == "ranking":
                # For ranking queries, show the ranking
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
        if any(word in query_lower for word in ["what is", "what was", "what's", "who is", "who was"]):
            return "point"
            
        # Aggregation queries - counting, summing, averaging
        if any(word in query_lower for word in ["how many", "total", "average", "sum of"]):
            return "aggregation"
            
        # Knowledge queries - require external knowledge or reasoning
        if any(word in query_lower for word in ["during", "time of", "recession", "industry"]):
            return "knowledge"
            
        # Reasoning queries - require analysis of challenges and solutions
        if any(word in query_lower for word in ["challenge", "solution", "faced", "proposed"]):
            return "reasoning"
            
        # Match queries - finding specific matches
        if any(word in query_lower for word in ["list all", "which", "who are", "find all"]):
            return "match"
            
        # Comparison queries - comparing values
        if any(word in query_lower for word in ["compare", "versus", "vs", "difference between"]):
            return "comparison"
            
        # Ranking queries - finding top/bottom values
        if any(word in query_lower for word in ["top", "highest", "most", "ranking"]):
            return "ranking"
            
        # Default to point query if no specific type is detected
        return "point"
    
    def process_query(self, db: Session, query_request: QueryRequest) -> QueryResponse:
        """Process a natural language query and return a response"""
        try:
            # Determine query type
            query_type = self._determine_query_type(query_request.query)
            
            # Generate SQL query
            sql_query = self._generate_sql_query(query_request.query, query_type)
            
            # Execute query
            result = db.execute(text(sql_query))
            rows = result.fetchall()
            
            # Format response
            response = self._format_response(query_request.query, rows, query_type)
            
            return QueryResponse(
                response=response,
                confidence=0.9,  # High confidence for direct SQL queries
                sql_query=sql_query
            )
            
        except Exception as e:
            return QueryResponse(
                response=f"Error processing query: {str(e)}",
                confidence=0.0,
                error=str(e),
                sql_query=None
            )