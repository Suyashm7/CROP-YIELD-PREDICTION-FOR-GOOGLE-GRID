import streamlit as st
import pandas as pd
import os

# Function to get all Parquet files from "data/parquet/" directory
def get_parquet_files():
    return [f for f in os.listdir("data/parquet") if f.endswith('.parquet')]

# Function to extract country name from filename
def extract_country_name(filename):
    return filename.replace('maize_', '').replace('.parquet', '')

# Load and preprocess data for all countries from Parquet
@st.cache_data
def load_all_data():
    """
    Loads all country data from parquet files and processes them
    Returns a dataframe with all countries' yield data
    """
    parquet_files = get_parquet_files()
    all_data = []

    for file in parquet_files:
        df = pd.read_parquet(f"data/parquet/{file}")
        country = extract_country_name(file)

        # Ensure required columns exist
        required_columns = {'Day', 'Country', 'yield', 'year'}
        if required_columns.issubset(df.columns):
            df['year'] = df['year']+1601
            all_data.append(df)

    return pd.concat(all_data)

# Function to get all CSV files from "predictions/" directory
def get_prediction_parquet_files():
    return [f for f in os.listdir("data/Parquet_Predictions") if f.endswith('.parquet')]

# Function to load and preprocess all prediction data from CSV files
@st.cache_data
def load_all_predictions():
    """
    Loads all prediction data from CSV files in the 'predictions' folder.
    Returns a dataframe with all prediction data.
    """
    csv_files = get_prediction_parquet_files()
    all_predictions = []

    for file in csv_files:
        df = pd.read_parquet(f"data/Parquet_Predictions/{file}")
        
        # Optional: Extract metadata like country name if useful
        # country = extract_country_name(file)  # reuse if applicable
        # df['Country'] = country
        
        # Ensure expected columns are present before appending
        if {'Day', 'Country', 'yield', 'year'}.issubset(df.columns):
            df['year'] = df['year'] + 1601
            all_predictions.append(df)

    return pd.concat(all_predictions)
