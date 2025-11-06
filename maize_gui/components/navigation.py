import streamlit as st

def display_navigation():
    """
    Display the main navigation sidebar with buttons for different pages
    """
    st.sidebar.header("Navigation")

    # Navigation buttons
    if st.sidebar.button("Country-wise Analysis"):
        st.session_state['page'] = 'country_analysis'

    if st.sidebar.button("Predicted Country-wise Analysis"):
        st.session_state['page'] = 'predicted_country_analysis'
    
    if st.sidebar.button("India-wise Analysis"):
        st.session_state['page'] = 'india_analysis'
    
    if st.sidebar.button("Predicted India-wise Analysis"):
        st.session_state['page'] = 'predicted_india_analysis'

    if st.sidebar.button("Regression Analysis"):
        st.session_state['page'] = 'regression_analysis'

    if st.sidebar.button("Predicted Regression Analysis"):
        st.session_state['page'] = 'predicted_regression_analysis'
    
    if st.sidebar.button("Visualize Model"):
        st.session_state['page'] = 'visualize_model'