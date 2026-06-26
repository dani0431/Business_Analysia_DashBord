"""
profiler.py
Computes statistical profile of the dataset: summary stats, missing values,
correlations, and a compact text summary suitable for feeding to an LLM.
"""

import pandas as pd
import numpy as np


def profile_dataframe(df: pd.DataFrame, column_types: dict) -> dict:
    """
    Build a structured statistical profile of the dataframe.
    """
    profile = {
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "missing_pct": {},
        "numeric_summary": {},
        "categorical_summary": {},
        "correlations": None,
    }

    # Missing values per column
    for col in df.columns:
        pct = df[col].isna().mean() * 100
        profile["missing_pct"][col] = round(pct, 2)

    # Numeric summary stats
    for col in column_types["numeric"]:
        series = df[col].dropna()
        if series.empty:
            continue
        profile["numeric_summary"][col] = {
            "mean": round(series.mean(), 2),
            "median": round(series.median(), 2),
            "std": round(series.std(), 2),
            "min": round(series.min(), 2),
            "max": round(series.max(), 2),
        }

    # Categorical summary: top values
    for col in column_types["categorical"]:
        counts = df[col].value_counts(dropna=True).head(5)
        profile["categorical_summary"][col] = counts.to_dict()

    # Correlation matrix for numeric columns
    if len(column_types["numeric"]) >= 2:
        corr = df[column_types["numeric"]].corr(numeric_only=True)
        profile["correlations"] = corr.round(2)

    return profile


def get_top_correlations(corr_matrix: pd.DataFrame, top_n: int = 5) -> list[tuple]:
    """
    Extract the top N strongest correlations (excluding self-correlation)
    from a correlation matrix.
    """
    if corr_matrix is None:
        return []

    pairs = []
    cols = corr_matrix.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr_matrix.iloc[i, j]
            if pd.notna(val):
                pairs.append((cols[i], cols[j], val))

    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    return pairs[:top_n]


def profile_to_text_summary(df: pd.DataFrame, column_types: dict, profile: dict) -> str:
    """
    Convert the statistical profile into a compact text summary
    suitable for sending to an LLM (keeps token usage low, no raw rows).
    """
    lines = []
    lines.append(f"Dataset shape: {profile['n_rows']} rows x {profile['n_cols']} columns.")
    lines.append(f"Columns: {', '.join(df.columns)}")
    lines.append(f"Numeric columns: {', '.join(column_types['numeric']) or 'none'}")
    lines.append(f"Categorical columns: {', '.join(column_types['categorical']) or 'none'}")
    lines.append(f"Datetime columns: {', '.join(column_types['datetime']) or 'none'}")

    lines.append("\nMissing data (% per column, only columns with >0% shown):")
    missing_lines = [
        f"  - {col}: {pct}%"
        for col, pct in profile["missing_pct"].items()
        if pct > 0
    ]
    lines.append("\n".join(missing_lines) if missing_lines else "  None")

    if profile["numeric_summary"]:
        lines.append("\nNumeric column statistics:")
        for col, stats in profile["numeric_summary"].items():
            lines.append(
                f"  - {col}: mean={stats['mean']}, median={stats['median']}, "
                f"std={stats['std']}, min={stats['min']}, max={stats['max']}"
            )

    if profile["categorical_summary"]:
        lines.append("\nTop categorical values:")
        for col, top_vals in profile["categorical_summary"].items():
            vals_str = ", ".join(f"{k} ({v})" for k, v in top_vals.items())
            lines.append(f"  - {col}: {vals_str}")

    if profile["correlations"] is not None:
        top_corrs = get_top_correlations(profile["correlations"])
        if top_corrs:
            lines.append("\nStrongest correlations between numeric columns:")
            for col_a, col_b, val in top_corrs:
                lines.append(f"  - {col_a} vs {col_b}: r = {val}")

    # Sample rows (small, just for context — not the full dataset)
    lines.append("\nSample rows (first 5):")
    lines.append(df.head(5).to_string(index=False))

    return "\n".join(lines)
