import os
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import duckdb

# Add root directory to PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sql_agent import SQLAgent
from src.rag_agent import RAGAgent
from src.ml_pipeline import MLPipeline

app = FastAPI(
    title="Enterprise Supply Chain Intelligence API",
    version="1.0.0",
    description="Asynchronous APIs for SQL Analytics, SLA RAG, and Risk Predictive Services."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate Agents
sql_agent = SQLAgent()
rag_agent = RAGAgent()
ml_pipeline = MLPipeline()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "warehouse_logs.duckdb")

# Input Schemas (Pydantic v2 Compliant)
class SQLQueryRequest(BaseModel):
    query: str = Field(description="What are the top 3 delayed vendors by average delay time?")

class RAGQueryRequest(BaseModel):
    query: str = Field(description="What is the penalty if vendor delay exceeds 5 days?")

class VendorRiskRequest(BaseModel):
    delivery_days: int = Field(default=8)
    promised_days: int = Field(default=5)
    shipment_cost: float = Field(default=5500.0)
    defect_rate: float = Field(default=3.2)

@app.get("/")
def root():
    return {"status": "healthy", "service": "Supply Chain Copilot API"}

@app.post("/api/query-sql")
def handle_sql_query(payload: SQLQueryRequest):
    df, generated_sql = sql_agent.execute_text_to_sql(payload.query)
    return {
        "generated_sql": generated_sql,
        "results": df.to_dict(orient="records")
    }

@app.post("/api/query-rag")
def handle_rag_query(payload: RAGQueryRequest):
    return rag_agent.query_sla_policy(payload.query)

@app.post("/api/predict-risk")
def handle_predict_risk(payload: VendorRiskRequest):
    return ml_pipeline.predict_vendor_risk(
        payload.delivery_days, payload.promised_days, payload.shipment_cost, payload.defect_rate
    )

@app.get("/api/dashboard-summary")
def get_dashboard_summary():
    conn = duckdb.connect(DB_PATH)
    
    res_shipments = conn.execute("SELECT COUNT(*) FROM vendor_deliveries").fetchone()
    res_delay = conn.execute("SELECT AVG(delivery_days - promised_days) FROM vendor_deliveries").fetchone()
    res_cost = conn.execute("SELECT SUM(shipment_cost) FROM vendor_deliveries").fetchone()
    res_churn = conn.execute("SELECT AVG(churn_risk) * 100 FROM customer_orders").fetchone()
    
    conn.close()

    total_shipments = res_shipments[0] if res_shipments else 0
    avg_delay = res_delay[0] if res_delay else 0.0
    total_cost = res_cost[0] if res_cost else 0.0
    churn_rate = res_churn[0] if res_churn else 0.0

    return {
        "total_shipments": int(total_shipments),
        "avg_delay_days": round(float(avg_delay), 2),
        "total_spend": round(float(total_cost), 2),
        "churn_rate_percent": round(float(churn_rate), 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)