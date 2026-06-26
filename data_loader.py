"""
data_loader.py
Handles uploading and parsing CSV/Excel files into a clean pandas DataFrame.
"""

import pandas as pd
import streamlit as st


def load_data(uploaded_file) -> pd.DataFrame | None:
    """
    Load a CSV or Excel file uploaded via Streamlit's file_uploader
    into a pandas DataFrame. Returns None and shows an error if loading fails.
    """
    if uploaded_file is None:
        return None

    filename = uploaded_file.name.lower()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a CSV or Excel file.")
            return None
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        return None

    if df.empty:
        st.warning("The uploaded file is empty.")
        return None

    df = clean_columns(df)
    return df


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleanup: strip whitespace from column names, drop fully empty columns/rows,
    and attempt to parse obvious date columns.
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Drop columns/rows that are entirely empty
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")

    # Try to auto-detect date-like columns by name
    for col in df.columns:
        if any(key in col.lower() for key in ["date", "time", "created", "updated"]):
            try:
                df[col] = pd.to_datetime(df[col], errors="ignore")
            except Exception:
                pass

    return df


def get_column_types(df: pd.DataFrame) -> dict:
    """
    Classify columns into numeric, categorical, and datetime buckets.
    """
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    datetime_cols = df.select_dtypes(include="datetime").columns.tolist()
    categorical_cols = [
        c for c in df.columns if c not in numeric_cols and c not in datetime_cols
    ]

    return {
        "numeric": numeric_cols,
        "categorical": categorical_cols,
        "datetime": datetime_cols,
    }
