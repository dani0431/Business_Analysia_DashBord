"""
app.py
Main Streamlit entry point for the AI Business Analysis Dashboard.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd

from data_loader import load_data, get_column_types
from profiler import profile_dataframe, profile_to_text_summary
from ai_insights import get_ai_insights
from charts import (
    bar_chart_top_categories,
    histogram_numeric,
    correlation_heatmap,
    time_series_line,
    scatter_plot,
)

st.set_page_config(page_title="AI Business Dashboard", layout="wide")

st.title("📊 AI-Powered Business Analysis Dashboard")
st.caption("Upload your company's dataset (CSV or Excel) to get instant statistics, charts, and AI-generated business insights.")

# ---------- Sidebar: Upload ----------
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is None:
    st.info("👈 Upload a CSV or Excel file from the sidebar to get started.")
    st.stop()

df = load_data(uploaded_file)
if df is None:
    st.stop()

column_types = get_column_types(df)

# ---------- Overview ----------
st.subheader("Data Preview")
st.dataframe(df.head(20), use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("Rows", f"{len(df):,}")
col2.metric("Columns", len(df.columns))
col3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")

# ---------- Statistical Profile ----------
profile = profile_dataframe(df, column_types)
profile_text = profile_to_text_summary(df, column_types, profile)

with st.expander("View raw statistical profile (sent to AI)"):
    st.text(profile_text)

# ---------- Charts ----------
st.subheader("📈 Visual Analysis")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if column_types["categorical"]:
        cat_col = st.selectbox("Categorical column", column_types["categorical"], key="cat_select")
        st.plotly_chart(bar_chart_top_categories(df, cat_col), use_container_width=True)
    else:
        st.info("No categorical columns detected.")

with chart_col2:
    if column_types["numeric"]:
        num_col = st.selectbox("Numeric column", column_types["numeric"], key="num_select")
        st.plotly_chart(histogram_numeric(df, num_col), use_container_width=True)
    else:
        st.info("No numeric columns detected.")

if profile["correlations"] is not None:
    st.plotly_chart(correlation_heatmap(profile["correlations"]), use_container_width=True)

if column_types["datetime"] and column_types["numeric"]:
    st.markdown("#### Time Series")
    date_col = st.selectbox("Date column", column_types["datetime"], key="date_select")
    value_col = st.selectbox("Value column", column_types["numeric"], key="value_select")
    st.plotly_chart(time_series_line(df, date_col, value_col), use_container_width=True)

if len(column_types["numeric"]) >= 2:
    st.markdown("#### Scatter Plot")
    sc1, sc2 = st.columns(2)
    with sc1:
        x_col = st.selectbox("X axis", column_types["numeric"], key="x_select")
    with sc2:
        y_col = st.selectbox(
            "Y axis",
            [c for c in column_types["numeric"] if c != x_col],
            key="y_select",
        )
    color_col = None
    if column_types["categorical"]:
        color_col = st.selectbox(
            "Color by (optional)",
            [None] + column_types["categorical"],
            key="color_select",
        )
    st.plotly_chart(scatter_plot(df, x_col, y_col, color_col), use_container_width=True)

# ---------- AI Insights ----------
st.subheader("🤖 AI Business Insights")

if st.button("Generate AI Insights"):
    with st.spinner("Analyzing your data with AI..."):
        result = get_ai_insights(profile_text)

    if "error" in result:
        st.error(result["error"])
        if "raw" in result:
            st.text(result["raw"])
    else:
        st.markdown(f"**Summary:** {result.get('summary', '')}")

        st.markdown("#### Key Insights")
        type_icons = {
            "trend": "📈",
            "anomaly": "⚠️",
            "opportunity": "💡",
            "risk": "🚨",
        }
        for insight in result.get("insights", []):
            icon = type_icons.get(insight.get("type", ""), "🔹")
            with st.container(border=True):
                st.markdown(f"{icon} **{insight.get('title', '')}**")
                st.write(insight.get("detail", ""))

        st.markdown("#### Recommendations")
        for rec in result.get("recommendations", []):
            st.markdown(f"- {rec}")
else:
    st.caption("Click the button above to generate AI-powered insights from your data profile.")
