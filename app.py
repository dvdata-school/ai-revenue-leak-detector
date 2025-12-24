import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Revenue Leak Detector",
    layout="wide"
)

st.title("💰 Revenue Leak Detector")
st.caption("Identify revenue risks before they become losses")

# ---------------- LOAD DATA ----------------
DATA_FILE = Path(__file__).parent / "AI_Revenue_Leak_Dataset_Processed.xls"

df = pd.read_excel(DATA_FILE)

df.columns = df.columns.str.strip().str.replace(" ", "_")

st.write("Detected columns:", list(df.columns))
st.stop()


# ---------------- DATA NORMALIZATION ----------------
df["Due_Date"] = pd.to_datetime(df["Due_Date"], errors="coerce")
df["Days_Late"] = pd.to_numeric(df["Days_Late"], errors="coerce").fillna(0)
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
df["Estimated_Loss"] = pd.to_numeric(df["Estimated_Loss"], errors="coerce").fillna(df["Amount"])

# ---------------- BUSINESS LOGIC ----------------

# Risk components
df["Delay_Risk"] = df["Days_Late"].apply(lambda x: 1 if x >= 30 else 0)
df["Status_Risk"] = df["Status"].apply(lambda x: 1 if x in ["Late", "Unpaid"] else 0)
df["High_Value_Risk"] = df["Amount"].apply(lambda x: 1 if x >= 5000 else 0)

df["Client_Risk_Score"] = df["Client_Risk"].map({
    "High": 3,
    "Medium": 2,
    "Low": 1
}).fillna(1)

# ---------------- LEAK SCORE (OWNED LOGIC) ----------------
df["Leak_Score"] = (
    0.4 * df["Delay_Risk"] +
    0.3 * df["Status_Risk"] +
    0.2 * df["High_Value_Risk"] +
    0.1 * df["Client_Risk_Score"]
)

# ---------------- EXPLANATIONS ----------------
def build_reasons(row):
    reasons = []
    if row["Delay_Risk"]:
        reasons.append(f"{int(row['Days_Late'])} days overdue")
    if row["Status_Risk"]:
        reasons.append(f"Status: {row['Status']}")
    if row["High_Value_Risk"]:
        reasons.append("High invoice value")
    if row["Client_Risk"] == "High":
        reasons.append("High-risk client history")
    return ", ".join(reasons)

df["Leak_Reasons"] = df.apply(build_reasons, axis=1)

# ---------------- ACTION RECOMMENDATIONS ----------------
def recommend_action(row):
    if row["Status"] == "Unpaid" and row["Days_Late"] >= 30:
        return "Immediate collections escalation"
    if row["Status"] == "Late":
        return "Send reminder + schedule follow-up"
    if row["Client_Risk"] == "High":
        return "Review contract & payment terms"
    return "Monitor"

df["Recommended_Action"] = df.apply(recommend_action, axis=1)

# ---------------- FILTERS ----------------
st.sidebar.header("Filters")

risk_filter = st.sidebar.selectbox(
    "Client Risk",
    ["All", "High", "Medium", "Low"]
)

status_filter = st.sidebar.multiselect(
    "Invoice Status",
    ["Paid", "Late", "Unpaid"],
    default=["Late", "Unpaid"]
)

df_filtered = df.copy()

if risk_filter != "All":
    df_filtered = df_filtered[df_filtered["Client_Risk"] == risk_filter]

df_filtered = df_filtered[df_filtered["Status"].isin(status_filter)]

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "Invoices at Risk",
    len(df_filtered)
)

col2.metric(
    "Potential Revenue at Risk",
    f"€{df_filtered['Estimated_Loss'].sum():,.0f}"
)

col3.metric(
    "High-Risk Clients",
    df_filtered[df_filtered["Client_Risk"] == "High"]["Client"].nunique()
)

# ---------------- PRIORITY TABLE ----------------
st.subheader("🚨 Top Revenue Leak Risks")

priority_view = df_filtered[
    [
        "Client",
        "Invoice_ID",
        "Amount",
        "Days_Late",
        "Leak_Score",
        "Leak_Reasons",
        "Recommended_Action"
    ]
].sort_values(by="Leak_Score", ascending=False).head(5)

st.dataframe(priority_view, use_container_width=True)

# ---------------- FULL DATA ----------------
with st.expander("View Full Dataset"):
    st.dataframe(df_filtered, use_container_width=True)





