import os
import duckdb
import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DATA_DIR, "warehouse_logs.duckdb")
SLA_TXT_PATH = os.path.join(DATA_DIR, "vendor_sla_policy.txt")

def generate_database():
    """Generates synthetic DuckDB tables for logistics and customer analytics."""
    print("Generating DuckDB Database...")
    conn = duckdb.connect(DB_PATH)
    
    # 1. Vendor Deliveries Dataset
    n_deliveries = 1000
    vendors = [
        ("VND_001", "Apex Logistics"),
        ("VND_002", "Global Freight Corp"),
        ("VND_003", "Swift Express"),
        ("VND_004", "Titan Transports"),
        ("VND_005", "Nexus Supply Solutions")
    ]
    
    vendor_choices = [vendors[i] for i in np.random.choice(len(vendors), n_deliveries)]
    promised_days = np.random.randint(2, 10, n_deliveries)
    # Delays added with random normal noise
    actual_days = promised_days + np.random.choice([0, 1, 2, 4, 7], n_deliveries, p=[0.5, 0.25, 0.15, 0.07, 0.03])
    delayed_status = np.where(actual_days > promised_days, 1, 0)
    shipment_cost = np.round(np.random.uniform(500, 15000, n_deliveries), 2)
    defect_rate = np.round(np.random.beta(2, 20, n_deliveries) * 100, 2)
    
    vendor_df = pd.DataFrame({
        "delivery_id": [f"DEL_{i+10000}" for i in range(n_deliveries)],
        "vendor_id": [v[0] for v in vendor_choices],
        "vendor_name": [v[1] for v in vendor_choices],
        "delivery_days": actual_days,
        "promised_days": promised_days,
        "delayed_status": delayed_status,
        "shipment_cost": shipment_cost,
        "defect_rate": defect_rate
    })
    
    conn.execute("DROP TABLE IF EXISTS vendor_deliveries")
    conn.execute("CREATE TABLE vendor_deliveries AS SELECT * FROM vendor_df")

    # 2. Customer Orders Dataset
    n_customers = 500
    order_value = np.round(np.random.uniform(100, 5000, n_customers), 2)
    return_rate = np.round(np.random.beta(1, 10, n_customers) * 100, 2)
    support_tickets = np.random.poisson(lam=2, size=n_customers)
    # Synthetic target: higher tickets & return rates drive churn risk
    churn_prob = 1 / (1 + np.exp(-( -2.0 + 0.3 * support_tickets + 0.05 * return_rate )))
    churn_risk = np.where(churn_prob > 0.4, 1, 0)

    customer_df = pd.DataFrame({
        "customer_id": [f"CUST_{i+1000}" for i in range(n_customers)],
        "order_value": order_value,
        "return_rate": return_rate,
        "support_tickets": support_tickets,
        "churn_risk": churn_risk
    })

    conn.execute("DROP TABLE IF EXISTS customer_orders")
    conn.execute("CREATE TABLE customer_orders AS SELECT * FROM customer_df")
    
    conn.close()
    print(f"DuckDB database populated successfully at {DB_PATH}")

def generate_sla_document():
    """Generates synthetic unstructured SLA Policy context document."""
    sla_text = """
    ENTERPRISE LOGISTICS & VENDOR SERVICE LEVEL AGREEMENT (SLA) GUIDELINES
    
    Section 1: Delivery Schedules and Compliance
    1.1 Standard Lead Time: Vendors must strictly adhere to the promised delivery lead times agreed upon in purchase orders.
    1.2 Grace Period: A maximum grace period of 24 hours is permitted under severe weather conditions, provided written notice is submitted 12 hours prior.

    Section 2: Delay Penalties & Refund Rules
    2.1 Clause 4.2 - Financial Penalties: Financial penalties apply automatically if delivery delay exceeds 5 calendar days. The vendor shall be liable for a compulsory 10% refund on total shipment invoice cost.
    2.2 Severe Delays (>10 Days): Delays exceeding 10 business days constitute a material breach of contract. The enterprise reserves the right to terminate the vendor agreement instantly and impose a 25% liquidated damages surcharge.

    Section 3: Quality Control & Defect Thresholds
    3.1 Allowable Defect Limit: Vendor shipments must maintain a defect rate under 2.5% per batch.
    3.2 Excessive Defect Penalties: If defect rates exceed 5.0% across two consecutive quarters, the vendor will be relegated to Tier-3 status and placed on mandatory probation.
    
    Section 4: Customer Return Policy & Escalations
    4.1 Support Ticket Thresholds: Customers experiencing high return rates (>8%) and submitting more than 3 support tickets are automatically flagged for executive retention review.
    """
    with open(SLA_TXT_PATH, "w") as f:
        f.write(sla_text.strip())
    print(f"SLA document created at {SLA_TXT_PATH}")

if __name__ == "__main__":
    generate_database()
    generate_sla_document()