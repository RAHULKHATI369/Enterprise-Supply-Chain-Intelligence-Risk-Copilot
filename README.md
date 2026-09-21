# 🚚 Enterprise Supply Chain Intelligence & Risk Copilot
> **AI-Powered Real-Time Logistics Analytics, Natural Language Text-to-SQL, Policy RAG, and ML Predictive Risk Assessment System.**

---

## 📌 Executive Overview

In large-scale enterprise operations (e.g., Retail, Automotive, E-commerce, Freight Logistics), managing supply chain risks across thousands of vendors and daily shipments is extremely challenging. Late deliveries, defective inventory, vendor SLA non-compliance, and customer escalations directly lead to millions of dollars in financial losses and increased customer churn.

**Enterprise Supply Chain Intelligence & Risk Copilot** is a unified AI Operations Center designed to solve these exact challenges. It brings together **Structured Business Analytics (Text-to-SQL)**, **Unstructured SLA Policy Knowledge (RAG)**, and **Predictive Machine Learning (Risk Engine)** into a single, high-performance Streamlit Dashboard.

---

## 🎯 Key Business Capabilities & Features

### 📊 1. Executive Performance Dashboard
* **Logistics KPI Center:** Real-time metrics for total shipments, average delivery delays, logistics spend, and customer churn rates.
* **Vendor Risk Matrix:** Interactive scatter visualization highlighting vendors with high defect rates and frequent delivery delays.
* **Customer Support Escalation Tracker:** Direct tracking of late delivery complaints linked to individual orders.

### 💬 2. Natural Language Text-to-SQL Query Agent
* **Zero-SQL Data Access:** Non-technical domain managers can ask complex business questions in plain English (e.g., *"Which vendor has the highest defect rate and average delay?"*).
* **Automated Query Generation:** Converts natural language inputs into optimized SQL statements execution against DuckDB enterprise data warehouse logs.
* **Instant Dynamic Dataframes:** Displays tabular query responses directly in the UI.

### 📚 3. RAG Knowledge Agent (SLA & Legal Policy Retrieval)
* **Contract & Policy Semantic Search:** Retrieves exact penalty clauses and operational guidelines from unstructured vendor agreements and SLA documentations.
* **Context-Aware Recommendations:** Answers queries such as *"What are the exact penalty percentages if vendor delay exceeds 5 days?"* with citation from official policy text.

### 🔮 4. Real-Time ML Predictive Risk Engine
* **Proactive Risk Scoring:** Machine Learning model trained on historical supply chain metrics predicts the likelihood of shipment failure or extreme delays before the order is delivered.
* **Interactive What-If Simulation:** Dynamic gauge indicators and slider controls allow users to simulate promised vs. actual delivery days, defect rates, and invoice values to assess real-time risk scores.

---

## ⚙️ System Architecture

```text
               +-------------------------------------------------------+
               |                  STREAMLIT FRONTEND                   |
               |        (Executive UI / Risk Gauge / Query Chat)       |
               +-------------------------------------------------------+
                                           |
                                           v
               +-------------------------------------------------------+
               |                  FASTAPI BACKEND API                  |
               +-------------------------------------------------------+
                /                          |                          \
               /                           |                           \
              v                            v                            v
   +--------------------+       +--------------------+       +--------------------+
   |   Text-to-SQL      |       |    RAG Engine      |       |  ML Risk Engine    |
   | (LLM + DuckDB Logs)|       | (Vector / SLA Doc) |       | (Scikit-Learn ML)  |
   +--------------------+       +--------------------+       +--------------------+
