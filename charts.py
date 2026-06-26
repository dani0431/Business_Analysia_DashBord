"""
charts.py
Reusable Plotly chart builders for the dashboard.
"""

import pandas as pd
import plotly.express as px


def bar_chart_top_categories(df: pd.DataFrame, col: str, top_n: int = 10):
    counts = df[col].value_counts(dropna=True).head(top_n).reset_index()
    counts.columns = [col, "count"]
    fig = px.bar(
        counts,
        x=col,
        y="count",
        title=f"Top {top_n} values in '{col}'",
        text="count",
    )
    fig.update_layout(margin=dict(t=40, b=10))
    return fig


def histogram_numeric(df: pd.DataFrame, col: str):
    fig = px.histogram(df, x=col, title=f"Distribution of '{col}'", nbins=30)
    fig.update_layout(margin=dict(t=40, b=10))
    return fig


def correlation_heatmap(corr_matrix: pd.DataFrame):
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        title="Correlation Heatmap (numeric columns)",
        aspect="auto",
    )
    fig.update_layout(margin=dict(t=40, b=10))
    return fig


def time_series_line(df: pd.DataFrame, date_col: str, value_col: str):
    plot_df = df[[date_col, value_col]].dropna().sort_values(date_col)
    fig = px.line(
        plot_df,
        x=date_col,
        y=value_col,
        title=f"'{value_col}' over time ({date_col})",
    )
    fig.update_layout(margin=dict(t=40, b=10))
    return fig


def scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, color_col: str | None = None):
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col if color_col else None,
        title=f"'{y_col}' vs '{x_col}'",
        trendline="ols" if df[x_col].dtype.kind in "if" else None,
    )
    fig.update_layout(margin=dict(t=40, b=10))
    return fig
