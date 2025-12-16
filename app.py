import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="AI Revenue Leak Detector", layout="wide")

# Load dataset
DATA_FILE = Path(__file__).parent / "AI_Revenue_Leak_Dataset_Processed.csv"
df = pd.read_csv(DATA_FILE)

# Normalize column names
df.columns = df.columns.str.strip()               # remove leading/trailing spaces
df.columns = df.columns.str.replace(" ", "_")    # replace spaces with underscores

st.title("💰 AI Revenue Leak Detector")

# Check available columns
st.write("Columns in dataset:", df.columns.tolist())

# Client Risk filter
risk_filter = st.selectbox(
    "Select Client Risk Level",
    ["All", "High", "Medium", "Low"]
)

df_filtered = df.copy()

if "Client_Risk" in df_filtered.columns:
    if risk_filter != "All":
        df_filtered = df_filtered[df_filtered["Client_Risk"] == risk_filter]
else:
    st.warning("'Client Risk' column not found in dataset!")

# Status filter
status_filter = st.multiselect(
    "Filter by Status",
    ["Paid", "Unpaid", "Late"],
    default=["Paid", "Unpaid", "Late"]
)

if "Status" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Status"].isin(status_filter)]
else:
    st.warning("'Status' column not found in dataset!")

# Display top revenue leaks
st.subheader("Top Revenue Leaks")
if "Leak_Score" in df_filtered.columns:
    st.dataframe(
        df_filtered.sort_values(by="Leak_Score", ascending=False).head(10),
        use_container_width=True
    )
else:
    st.warning("'Leak Score' column not found in dataset!")

# Revenue at risk metric
if "Estimated_Loss" in df_filtered.columns:
    st.metric("Revenue at Risk (€)", f"{df_filtered['Estimated_Loss'].sum():,.0f}")
else:
    st.warning("'Estimated Loss' column not found in dataset!")

# Show full dataset option
if st.checkbox("Show Full Dataset"):
    st.dataframe(df_filtered, use_container_width=True)
