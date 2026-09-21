import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os

# --- 1. BRANDING & ASSETS SETUP ---
LOGO_PATH = "assets/logo.png"

if os.path.exists(LOGO_PATH):
    app_logo = Image.open(LOGO_PATH)
else:
    app_logo = "🚚"  # Fallback emoji if image missing

# Set Page Config with Custom 3D Logo Icon
st.set_page_config(
    page_title="SC Copilot | Supply Chain Intelligence",
    page_icon=app_logo,
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000"

# --- 2. PROFESSIONAL SIDEBAR NAVIGATION ---
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    
    st.title("SC Copilot")
    st.caption("AI-Powered Supply Chain Risk Intelligence")
    st.markdown("---")
    
    # Navigation with icons
    page = st.radio(
        "Select View:", 
        [
            "📊 Executive Overview", 
            "🧠 Natural Language Analytics", 
            "🔮 Dynamic ML Risk Predictor"
        ]
    )

# Clean Navigation Page Names for Logic Checks
clean_page = page.replace("📊 ", "").replace("🧠 ", "").replace("🔮 ", "")

# --- 3. MAIN HEADER WITH BRANDING ---
header_col1, header_col2 = st.columns([0.08, 0.92])
with header_col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=65)
with header_col2:
    st.title("Enterprise Supply Chain Intelligence & Risk Copilot")
    st.caption("AI-powered SQL Analytics, SLA RAG Retrieval, and Dynamic Risk Scoring")

# Sidebar Icon Styling
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {padding-top: 0rem;}
        .main .block-container {padding-top: 2rem;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)
def fetch_summary():
    try:
        res = requests.get(f"{API_BASE_URL}/api/dashboard-summary", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    
    return {
        "total_shipments": 1000, 
        "avg_delay_days": 1.04, 
        "total_spend": 7670177.30, 
        "churn_rate_percent": 16.8
    }

# TAB 1: EXECUTIVE OVERVIEW
if clean_page == "Executive Overview":
    st.header("📊 Executive Performance Dashboard")
    metrics = fetch_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Shipments", f"{metrics.get('total_shipments', 1000):,}")
    col2.metric("Avg Delivery Delay", f"{metrics.get('avg_delay_days', 1.04)} Days")
    col3.metric("Total Logistics Spend", f"${metrics.get('total_spend', 7670177.30):,.2f}")
    col4.metric("Customer Churn Rate", f"{metrics.get('churn_rate_percent', 16.8)}%")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Vendor Delay vs. Defect Distribution")
        try:
            sql_res = requests.post(
                f"{API_BASE_URL}/api/query-sql", 
                json={"query": "SELECT vendor_name, delivery_days, defect_rate, shipment_cost FROM vendor_deliveries LIMIT 100"},
                timeout=5
            ).json()
            
            raw_data = sql_res.get("results") if "results" in sql_res else sql_res.get("data", [])
            df = pd.DataFrame(raw_data)
            
            if not df.empty:
                # If exact raw columns exist, plot detail chart
                if "delivery_days" in df.columns and "defect_rate" in df.columns:
                    fig = px.scatter(
                        df, 
                        x="delivery_days", 
                        y="defect_rate", 
                        color="vendor_name", 
                        size="shipment_cost" if "shipment_cost" in df.columns else None,
                        title="Shipment Cost vs. Delay & Defect Rate", 
                        hover_data=["vendor_name"]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                # Fallback plot for aggregated query response
                elif "avg_days" in df.columns and "avg_defect" in df.columns:
                    fig = px.scatter(
                        df, 
                        x="avg_days", 
                        y="avg_defect", 
                        color="vendor_name", 
                        title="Avg Delay vs. Avg Defect Rate", 
                        hover_data=["vendor_name"]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(df, use_container_width=True)
            else:
                st.info("No shipment data available.")
        except Exception as e:
            st.error(f"Error loading Vendor Delay Chart: {e}")

    with c2:
        st.subheader("Customer Support Escalations vs. Churn")
        try:
            sql_res_cust = requests.post(
                f"{API_BASE_URL}/api/query-sql", 
                json={"query": "SELECT support_tickets, return_rate, churn_risk FROM customer_orders LIMIT 200"},
                timeout=5
            ).json()
            
            raw_cust_data = sql_res_cust.get("results") if "results" in sql_res_cust else sql_res_cust.get("data", [])
            df_cust = pd.DataFrame(raw_cust_data)
            
            if not df_cust.empty:
                if "support_tickets" in df_cust.columns and "return_rate" in df_cust.columns:
                    fig2 = px.box(
                        df_cust, 
                        x="support_tickets", 
                        y="return_rate", 
                        color="churn_risk" if "churn_risk" in df_cust.columns else None,
                        labels={"churn_risk": "Churned"}, 
                        title="Impact of Support Tickets on Churn"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.dataframe(df_cust, use_container_width=True)
            else:
                st.info("No customer data available.")
        except Exception as e:
            st.error(f"Error loading Support Escalations Chart: {e}")

# TAB 2: NATURAL LANGUAGE ANALYTICS
elif clean_page == "Natural Language Analytics":
    st.header("🧠 Dual-Engine Natural Language Agent")
    
    tab_sql, tab_rag = st.tabs(["Structured Data (Text-to-SQL)", "Unstructured SLA Knowledge (RAG)"])

    with tab_sql:
        st.subheader("Query Warehouse SQL Database")
        sql_query = st.text_input(
            "Ask a question about vendors, shipments, or customers:", 
            value="Which vendor has the highest defect rate and average delay?"
        )
        
        if st.button("Execute SQL Agent"):
            with st.spinner("Translating text to SQL and querying DuckDB..."):
                try:
                    res = requests.post(f"{API_BASE_URL}/api/query-sql", json={"query": sql_query}, timeout=10).json()
                    st.code(res.get("generated_sql", "-- No SQL Generated"), language="sql")
                    
                    raw_res_data = res.get("results") if "results" in res else res.get("data", [])
                    df_res = pd.DataFrame(raw_res_data)
                    st.dataframe(df_res, use_container_width=True)
                except Exception as e:
                    st.error(f"Failed to execute SQL query: {e}")

    with tab_rag:
        st.subheader("Ask SLA & Contract Policy Documents")
        rag_query = st.text_input(
            "Ask about SLAs, rules, and penalties:", 
            value="What are the specific penalties if vendor delay exceeds 5 days?"
        )
        
        if st.button("Run RAG Retrieval"):
            with st.spinner("Searching Vector Store & Generating Response..."):
                try:
                    res = requests.post(f"{API_BASE_URL}/api/query-rag", json={"query": rag_query}, timeout=10).json()
                    st.markdown("### Answer")
                    st.write(res.get("answer", "No answer generated."))
                    st.caption(f"Sources: {', '.join(res.get('sources', []))}")
                except Exception as e:
                    st.error(f"Failed to retrieve SLA policy: {e}")

# TAB 3: DYNAMIC ML RISK PREDICTOR
elif clean_page == "Dynamic ML Risk Predictor":
    st.header("🔮 Real-Time Machine Learning Risk Assessment")
    
    col_in, col_out = st.columns([1, 1])

    with col_in:
        st.subheader("Vendor Order Parameters")
        promised = st.slider("Promised Delivery Lead Time (Days)", 1, 14, 5)
        actual = st.slider("Actual Estimated Delivery (Days)", 1, 20, 8)
        cost = st.number_input("Shipment Invoice Cost ($)", min_value=100.0, max_value=50000.0, value=7500.0)
        defect = st.slider("Batch Defect Rate (%)", 0.0, 10.0, 3.5, step=0.1)

    with col_out:
        st.subheader("Prediction Dashboard")
        if st.button("Calculate ML Delay Risk Score"):
            payload = {
                "delivery_days": actual,
                "promised_days": promised,
                "shipment_cost": cost,
                "defect_rate": defect
            }
            try:
                res = requests.post(f"{API_BASE_URL}/api/predict-risk", json=payload, timeout=5).json()
                score = res.get("risk_score", 0.0)
                level = res.get("risk_level", "NORMAL")

                gauge_val = score * 100 if score <= 1.0 else score

                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=gauge_val,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"Risk Level: {level}"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 40], 'color': "lightgreen"},
                            {'range': [40, 75], 'color': "yellow"},
                            {'range': [75, 100], 'color': "red"}
                        ]
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Failed to calculate ML risk: {e}")