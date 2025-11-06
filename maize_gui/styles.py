import streamlit as st

def apply_custom_styles():
    """
    Apply improved custom CSS styles to the application
    """
    st.markdown(
        """
        <style>
            .stButton>button {
                width: 100%;
                background-color: #FF4B4B;
                color: white;
                font-size: 18px;
                padding: 10px;
                border-radius: 8px;
                border: none;
                transition: background-color 0.3s ease, box-shadow 0.3s ease, transform 0.2s ease;
            }
            .stButton>button:hover {
                background-color: #D93D3D;
                color: #FFFFFF !important;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5);
                transform: scale(1.02);
            }
            .stButton {
                display: block;
                margin-bottom: 10px;
            }
            .hoverinfo {
                background-color: rgba(50, 50, 50, 0.9) !important;
                color: white !important;
                
                font-weight: bold;
            }
            .stSlider {
                width: 80% !important;
            }
            .filter-container {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
