import os
import duckdb
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "warehouse_logs.duckdb")

class MLPipeline:
    def __init__(self):
        self.vendor_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.churn_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.vendor_scaler = StandardScaler()
        self.churn_scaler = StandardScaler()
        self.train_models()

    def train_models(self):
        """Train models dynamically from DuckDB data."""
        conn = duckdb.connect(DB_PATH)
        
        # 1. Train Vendor Delay Risk Model
        df_vendor = conn.execute("SELECT delivery_days, promised_days, shipment_cost, defect_rate, delayed_status FROM vendor_deliveries").df()
        X_v = df_vendor[["delivery_days", "promised_days", "shipment_cost", "defect_rate"]]
        y_v = df_vendor["delayed_status"]
        
        X_v_scaled = self.vendor_scaler.fit_transform(X_v)
        self.vendor_model.fit(X_v_scaled, y_v)

        # 2. Train Customer Churn Model
        df_cust = conn.execute("SELECT order_value, return_rate, support_tickets, churn_risk FROM customer_orders").df()
        X_c = df_cust[["order_value", "return_rate", "support_tickets"]]
        y_c = df_cust["churn_risk"]
        
        X_c_scaled = self.churn_scaler.fit_transform(X_c)
        self.churn_model.fit(X_c_scaled, y_c)

        conn.close()

    def predict_vendor_risk(self, delivery_days: int, promised_days: int, shipment_cost: float, defect_rate: float) -> dict:
        features = pd.DataFrame([[delivery_days, promised_days, shipment_cost, defect_rate]], 
                                columns=["delivery_days", "promised_days", "shipment_cost", "defect_rate"])
        features_scaled = self.vendor_scaler.transform(features)
        risk_prob = float(self.vendor_model.predict_proba(features_scaled)[0][1])
        
        risk_level = "CRITICAL" if risk_prob > 0.75 else ("HIGH" if risk_prob > 0.4 else "NORMAL")
        return {"risk_score": round(risk_prob, 4), "risk_level": risk_level}

    def predict_churn(self, order_value: float, return_rate: float, support_tickets: int) -> dict:
        features = pd.DataFrame([[order_value, return_rate, support_tickets]], 
                                columns=["order_value", "return_rate", "support_tickets"])
        features_scaled = self.churn_scaler.transform(features)
        churn_prob = float(self.churn_model.predict_proba(features_scaled)[0][1])
        
        return {"churn_probability": round(churn_prob, 4), "high_churn_risk": churn_prob > 0.5}