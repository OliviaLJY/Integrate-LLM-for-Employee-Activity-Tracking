from openai import OpenAI
import os
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db import models
from ..schemas import QueryRequest, QueryResponse

class QueryProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def _generate_sql_query(self, natural_query: str, db_schema: str) -> str:
        """Convert natural language query to SQL using GPT-3.5-turbo"""
        prompt = f"""
        Given the following database schema:
        {db_schema}
        
        Convert this natural language query to SQL:
        {natural_query}
        
        If the query is about changing or updating data, use UPDATE or INSERT statements.
        If the query is about retrieving data, use SELECT statements.
        
        Return only the SQL query without any explanation.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        return response.choices[0].message.content.strip()
    
    def _format_response(self, query: str, results: Any) -> str:
        """Format database results into natural language using GPT-3.5-turbo"""
        prompt = f"""
        Given the following query:
        {query}
        
        And the results:
        {results}
        
        Provide a natural language summary of the results. Be concise but informative.
        If the query was about changing data, confirm the changes made.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def process_query(self, db: Session, query_request: QueryRequest) -> QueryResponse:
        # Get database schema
        db_schema = """
        Table: employees
        - id (Integer, primary key)
        - email (String, unique)
        - job_title (String)
        - department (String)
        - hire_date (Date)
        
        Table: employee_activities
        - id (Integer, primary key)
        - employee_id (Integer, foreign key to employees.id)
        - week_number (Integer)
        - meetings_attended (Integer)
        - total_sales (Float)
        - hours_worked (Float)
        - activities (Text)
        """
        
        try:
            # Generate SQL query
            sql_query = self._generate_sql_query(query_request.query, db_schema)
            
            # Execute query using SQLAlchemy text()
            if sql_query.strip().upper().startswith(('SELECT', 'WITH')):
                # For SELECT queries, fetch results
                results = db.execute(text(sql_query)).fetchall()
                answer = self._format_response(query_request.query, results)
            else:
                # For UPDATE/INSERT queries, execute and commit
                result = db.execute(text(sql_query))
                db.commit()
                answer = self._format_response(query_request.query, f"Query executed successfully. {result.rowcount} rows affected.")
            
            return QueryResponse(
                answer=answer,
                confidence=0.9,
                supporting_data={"sql_query": sql_query}
            )
            
        except Exception as e:
            return QueryResponse(
                answer=f"Error processing query: {str(e)}",
                confidence=0.0,
                supporting_data={"error": str(e)}
            ) 