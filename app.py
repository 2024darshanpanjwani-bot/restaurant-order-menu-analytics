
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Restaurant Analytics",
    page_icon="🍽️",
    layout="wide"
)

DB = Path("restaurant.db")

st.markdown("""
<style>
    .block-container {padding-top: 1.5rem;}
    div[data-testid="stMetric"] {
        background: #172B27;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #315247;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍽️ Restaurant Order & Menu Analytics")
st.caption("Data Engineering Project | ETL Pipeline + SQL Analytics")

if not DB.exists():
    st.error("Database not found. Run python3 generate_sample_data.py and python3 etl.py first.")
    st.stop()

with sqlite3.connect(DB) as conn:
    sales = pd.read_sql_query("SELECT * FROM clean_sales", conn)
    orders = pd.read_sql_query("SELECT * FROM orders", conn)
    menu = pd.read_sql_query("SELECT * FROM menu", conn)

if sales.empty:
    st.warning("No sales data found. Run the ETL pipeline first.")
    st.stop()

sales["order_date"] = pd.to_datetime(sales["order_date"])
completed = sales[sales["status"] == "Completed"].copy()

st.sidebar.header("Dashboard Filters")

min_date = completed["order_date"].min().date()
max_date = completed["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

categories = ["All Categories"] + sorted(
    completed["category"].dropna().unique().tolist()
)
category = st.sidebar.selectbox("Menu Category", categories)

filtered = completed.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        (filtered["order_date"].dt.date >= start_date)
        & (filtered["order_date"].dt.date <= end_date)
    ]

if category != "All Categories":
    filtered = filtered[filtered["category"] == category]

revenue = filtered["line_revenue"].sum()
order_count = filtered["order_id"].nunique()
avg_order = revenue / order_count if order_count else 0
units = filtered["quantity"].sum()

st.subheader("Business Overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"₹{revenue:,.0f}")
c2.metric("Completed Orders", f"{order_count:,}")
c3.metric("Average Order Value", f"₹{avg_order:,.2f}")
c4.metric("Units Sold", f"{units:,}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("📈 Daily Revenue Trend")
    daily = (
        filtered.groupby(filtered["order_date"].dt.date)["line_revenue"]
        .sum()
        .reset_index()
    )
    daily.columns = ["Date", "Revenue"]
    st.line_chart(daily, x="Date", y="Revenue", use_container_width=True)

with right:
    st.subheader("🍴 Revenue by Category")
    category_sales = (
        filtered.groupby("category")["line_revenue"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(category_sales, use_container_width=True)

left, right = st.columns(2)

with left:
    st.subheader("🏆 Best-Selling Dishes")
    best = (
        filtered.groupby("item_name")
        .agg(
            Units_Sold=("quantity", "sum"),
            Revenue=("line_revenue", "sum")
        )
        .sort_values("Units_Sold", ascending=False)
        .head(10)
        .reset_index()
    )
    st.dataframe(best, use_container_width=True, hide_index=True)

with right:
    st.subheader("💳 Payment Method Analysis")
    payment = (
        filtered.groupby("payment_method")["order_id"]
        .nunique()
        .sort_values(ascending=False)
        .reset_index()
    )
    payment.columns = ["Payment Method", "Orders"]
    st.bar_chart(payment, x="Payment Method", y="Orders")

st.divider()
st.subheader("⚙️ ETL Pipeline Monitor")

p1, p2, p3 = st.columns(3)
p1.success(f"EXTRACT\n\n{len(orders)} orders loaded")
p2.success(f"TRANSFORM\n\n{len(sales)} sales rows available")
p3.success(f"LOAD\n\nSQLite database connected")

st.subheader("🧹 Data Quality Summary")
q1, q2, q3 = st.columns(3)
q1.metric("Menu Items", len(menu))
q2.metric("Raw Order Items", len(pd.read_sql_query(
    "SELECT * FROM order_items", sqlite3.connect(DB)
)))
q3.metric("Cancelled Orders", int(
    (orders["status"] == "Cancelled").sum()
))

with st.expander("View filtered sales records"):
    st.dataframe(
        filtered.sort_values("order_date", ascending=False),
        use_container_width=True,
        hide_index=True
    )

st.caption("Restaurant Analytics Pipeline | Python · Pandas · SQLite · SQL · Streamlit")
