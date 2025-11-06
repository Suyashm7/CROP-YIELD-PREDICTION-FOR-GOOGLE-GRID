import streamlit as st # type: ignore
import pandas as pd # type: ignore
import os
from utils import load_all_data
from utils import load_all_predictions
from styles import apply_custom_styles
from components.navigation import display_navigation
from tabs.country_analysis import display_country_analysis
from tabs.predicted_country_analysis import display_predicted_country_analysis
from tabs.india_analysis import display_india_analysis
from tabs.predicted_india_analysis import display_predicted_india_analysis
from tabs.regression_analysis import display_regression_analysis
from tabs.predicted_regression_analysis import display_predicted_regression_analysis
from tabs.visualize_model import visualize_model

# Page Configuration
st.set_page_config(page_title="Global Maize Yield Trends", layout="wide")
st.title("🌽 Global Maize Yield Trends Dashboard")

# Apply custom CSS styles
apply_custom_styles()

# Initialize session state for navigation if not exists
if 'page' not in st.session_state:
    st.session_state['page'] = 'country_analysis'

# Load data
df_all_countries = load_all_data()
df_predicted = load_all_predictions()
india_data = df_all_countries[df_all_countries['Country'] == 'India']
predicted_india = df_predicted[df_predicted['Country'] == 'India']

# Display sidebar navigation
display_navigation()

# Display the selected page based on session state
if st.session_state['page'] == 'country_analysis':
    display_country_analysis(df_all_countries)
# Display the selected page based on session state
elif st.session_state['page'] == 'predicted_country_analysis':
    display_predicted_country_analysis(df_predicted)
elif st.session_state['page'] == 'india_analysis':
    display_india_analysis(india_data)
elif st.session_state['page'] == 'predicted_india_analysis':
    display_predicted_india_analysis(predicted_india)
elif st.session_state['page'] == 'regression_analysis':
    display_regression_analysis(india_data)
elif st.session_state['page'] == 'predicted_regression_analysis':
    display_predicted_regression_analysis(predicted_india)
elif st.session_state['page'] == 'visualize_model':
    visualize_model()

# Footer
st.markdown("---")
st.markdown("*Data sourced from agricultural yield records. Yields converted to Tons/Ha.*")