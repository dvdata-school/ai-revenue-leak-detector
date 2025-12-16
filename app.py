import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="AI Revenue Leak Detector", layout="wide")

DATA_FILE = Path(__file__).parent / "AI_Revenue_Leak_Dataset_Processed.csv"
df = pd.read_csv(DATA_FILE)

st.title("💰 AI Revenue Leak Detector")

risk_filter = st.selectbox(
    "Select Client Risk Level",
    ["All", "High", "Medium", "Low"]
)

df_filtered = df.copy()

if risk_filter != "All":
    df_filtered = df_filtered[df_filtered["Client Risk"] == risk_filter]

status_filter = st.multiselect(
    "Filter by Status",
    ["Paid", "Unpaid", "Late"],
    default=["Paid", "Unpaid", "Late"]
)

df_filtered = df_filtered[df_filtered["Status"].isin(status_filter)]

st.subheader("Top Revenue Leaks")
st.dataframe(
    df_filtered.sort_values(by="Leak Score", ascending=False).head(10),
    use_container_width=True
)

st.metric("Revenue at Risk (€)", f"{df_filtered['Estimated Loss'].sum():,.0f}")

if st.checkbox("Show Full Dataset"):
    st.dataframe(df_filtered, use_container_width=True)
