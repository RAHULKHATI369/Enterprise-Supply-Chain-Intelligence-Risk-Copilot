import os
from typing import Any, Optional, Tuple
import duckdb
import pandas as pd
import google.generativeai as genai

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "warehouse_logs.duckdb")

class SQLAgent:
    def __init__(self) -> None:
        self.api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.model: Optional[Any] = None

        if self.api_key:
            # Pylance-safe resolution for google.generativeai exports
            configure_fn = getattr(genai, "configure", None)
            model_cls = getattr(genai, "GenerativeModel", None)

            if configure_fn and model_cls:
                configure_fn(api_key=self.api_key)
                self.model = model_cls('gemini-1.5-flash')

    def execute_text_to_sql(self, user_query: str) -> Tuple[pd.DataFrame, str]:
        """Translates natural language to DuckDB SQL query and returns results."""
        if not self.model:
            # Fallback mock SQL response if API key is not present
            fallback_sql = "SELECT vendor_name, AVG(delivery_days) as avg_days, AVG(defect_rate) as avg_defect FROM vendor_deliveries GROUP BY vendor_name LIMIT 5;"
            return self._run_query(fallback_sql), fallback_sql

        prompt = f"""
        You are an expert DuckDB SQL Data Engineer. Translate the following user question into a syntactically valid DuckDB SQL query.
        
        Database Schema:
        1. Table: vendor_deliveries
           Columns: delivery_id (VARCHAR), vendor_id (VARCHAR), vendor_name (VARCHAR), delivery_days (INTEGER), promised_days (INTEGER), delayed_status (INTEGER), shipment_cost (DOUBLE), defect_rate (DOUBLE)
        
        2. Table: customer_orders
           Columns: customer_id (VARCHAR), order_value (DOUBLE), return_rate (DOUBLE), support_tickets (INTEGER), churn_risk (INTEGER)

        Rules:
        - Return ONLY the executable SQL query inside standard text.
        - Do not surround with markdown backticks or explanations.
        
        Question: {user_query}
        SQL Query:
        """
        try:
            response = self.model.generate_content(prompt)
            generated_sql = response.text.strip().replace("```sql", "").replace("```", "").strip()
            df = self._run_query(generated_sql)
            return df, generated_sql
        except Exception as e:
            # Fallback to general query upon parsing or execution failure
            fallback_sql = "SELECT * FROM vendor_deliveries ORDER BY delivery_days DESC LIMIT 5;"
            return self._run_query(fallback_sql), f"Error generating query ({str(e)}). Executing Fallback SQL: {fallback_sql}"

    def _run_query(self, sql: str) -> pd.DataFrame:
        conn = duckdb.connect(DB_PATH)
        try:
            df = conn.execute(sql).df()
        except Exception as e:
            df = pd.DataFrame({"Error": [str(e)]})
        finally:
            conn.close()
        return df