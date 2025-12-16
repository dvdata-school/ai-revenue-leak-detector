import streamlit as st
import pandas as pd

df = pd.read_csv("AI_Revenue_Leak_Dataset_Processed.csv")

st.title("💰 AI Revenue Leak Detector")

risk_filter = st.selectbox("Select Client Risk Level", ["All", "High", "Medium", "Low"])
if risk_filter != "All":
    df_filtered = df[df['Client Risk'] == risk_filter]
else:
    df_filtered = df.copy()

status_filter = st.multiselect("Filter by Status", ["Paid", "Unpaid", "Late"], default=["Paid", "Unpaid", "Late"])
df_filtered = df_filtered[df_filtered['Status'].isin(status_filter)]

st.subheader("Top Revenue Leaks")
st.dataframe(df_filtered.sort_values(by='Leak Score', ascending=False).head(10))

st.subheader("Total Revenue at Risk")
st.write("€", df_filtered['Estimated Loss'].sum())

if st.checkbox("Show Full Dataset"):
    st.dataframe(df_filtered)
