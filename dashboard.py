import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

API_URL = "http://localhost:8000/colleges"

st.set_page_config(page_title="Shiksha College Dashboard", layout="wide")
st.title("🎓 Shiksha.com Educational Data Platform")

@st.cache_data(ttl=600)
def fetch_colleges_data(params=None):
    try:
        resp = requests.get(API_URL, params=params or {})
        resp.raise_for_status()
        data = resp.json()
        return pd.DataFrame(data.get("colleges", []))
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def parse_money_to_lakhs(value_str):
    if not value_str or not isinstance(value_str, str):
        return None
    value_str = value_str.replace(",", "").lower()
    match = re.search(r'₹\s*([\d.]+)\s*(lakh|lac|crore)?', value_str)
    if match:
        amount = float(match.group(1))
        unit = match.group(2)
        if unit in ['lakh', 'lac']:
            return amount
        elif unit == 'crore':
            return amount * 100
        return amount
    return None

# Sidebar filters
st.sidebar.header("Filters")
name_filter = st.sidebar.text_input("College Name contains")

min_fee = st.sidebar.number_input("Min Fee (Lakhs)", min_value=0.0, value=0.0, step=0.1)
max_fee = st.sidebar.number_input("Max Fee (Lakhs)", min_value=0.0, value=100.0, step=0.1)

min_salary = st.sidebar.number_input("Min Salary (Lakhs)", min_value=0.0, value=0.0, step=0.1)
max_salary = st.sidebar.number_input("Max Salary (Lakhs)", min_value=0.0, value=100.0, step=0.1)

limit = st.sidebar.slider("Max Results", 10, 100, 50)

# Query params
query_params = {"limit": int(limit)}
if name_filter.strip():
    query_params["name"] = name_filter.strip()
if min_fee <= max_fee:
    query_params["min_fee"] = float(min_fee)
    query_params["max_fee"] = float(max_fee)
if min_salary <= max_salary:
    query_params["min_salary"] = float(min_salary)
    query_params["max_salary"] = float(max_salary)

# Fetch and preprocess
df = fetch_colleges_data(query_params)

if df.empty:
    st.warning("No colleges found matching the filters.")
    st.stop()

# Process salary & fee into numeric lakhs
df["fees_lakhs"] = df["fees"].map(parse_money_to_lakhs)
df["salary_lakhs"] = df["salary"].map(parse_money_to_lakhs)

# Display table without fees_lakhs or salary_lakhs
st.markdown(f"### Showing {len(df)} colleges")
st.dataframe(df[["name", "fees", "salary", "ranking"]])

# Visualization Section
st.markdown("---")
st.subheader("📊 Visualizations")

df_vis = df.copy()
df_vis = df_vis.dropna(subset=["ranking"])
df_vis["ranking"] = df_vis["ranking"].astype(int)

if df_vis["salary_lakhs"].notna().sum() > 0:
    st.markdown("#### 🎯 Ranking vs Salary")
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df_vis, x="ranking", y="salary_lakhs", s=100, ax=ax1)
    ax1.set_xlabel("Ranking")
    ax1.set_ylabel("Salary (Lakhs)")
    ax1.set_title("Ranking vs Salary")
    ax1.invert_xaxis()
    st.pyplot(fig1)

if df_vis["fees_lakhs"].notna().sum() > 0:
    st.markdown("#### 💰 Ranking vs Fees")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df_vis, x="ranking", y="fees_lakhs", s=100, ax=ax2)
    ax2.set_xlabel("Ranking")
    ax2.set_ylabel("Fees (Lakhs)")
    ax2.set_title("Ranking vs Fees")
    ax2.invert_xaxis()
    st.pyplot(fig2)


top_n = 10
top_df = df_vis.nsmallest(top_n, "ranking")
if not top_df.empty:
    st.markdown(f"#### 🏅 Top {top_n} Colleges: Salary + Fees")
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    x = top_df["name"]
    bar1 = ax4.barh(x, top_df["salary_lakhs"], color='green', label="Salary")
    bar2 = ax4.barh(x, top_df["fees_lakhs"], color='orange', left=top_df["salary_lakhs"], label="Fees")
    ax4.set_xlabel("Amount (Lakhs)")
    ax4.set_title("Top Colleges: Salary + Fees (Stacked)")
    ax4.legend()
    st.pyplot(fig4)

st.markdown("---")
st.caption("📌 Data source: Scraped from Shiksha.com via FastAPI backend")
