import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

def display_predicted_india_analysis(india_data):
    """
    Display the India-specific analysis page with optimized performance
    """
    st.subheader("India-wise Analysis")

    # Preprocess data once when page loads
    if 'india_preprocessed_data_1' not in st.session_state:
        with st.spinner("Processing India data... Please wait"):
            # Filter day 239 data once (used in both views)
            india_filtered = india_data[india_data['Day'] == 239].copy()
            
            # Get unique states if available
            has_state_data = 'State' in india_data.columns
            available_states = sorted(india_filtered['State'].unique()) if has_state_data else []
            
            # Prepare national trend data
            india_yearly = india_filtered.groupby('year')['yield'].mean().reset_index()
            
            # Prepare state-wise data if available
            if has_state_data:
                # Pre-compute state-year grouping
                state_year_data = india_filtered.groupby(['State', 'year'])['yield'].mean().reset_index()
                
                # Pre-compute state grouping
                state_data = india_filtered.groupby('State')['yield'].mean().reset_index()
            else:
                state_year_data = pd.DataFrame()
                state_data = pd.DataFrame()
            
            # Store in session states
            st.session_state['india_preprocessed_data_1'] = {
                'filtered_data': india_filtered,
                'has_state_data': has_state_data,
                'available_states': available_states,
                'national_yearly': india_yearly,
                'state_year_data': state_year_data,
                'state_data': state_data,
                'min_year': int(india_filtered['year'].min()),
                'max_year': int(india_filtered['year'].max())
            }

    # Sub-navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("State-wise Trend Analysis"):
            st.session_state['india_view'] = 'state_trend'
    with col2:
        if st.button("Bar Graph Analysis"):
            st.session_state['india_view'] = 'bar'

    # Default view
    if 'india_view' not in st.session_state:
        st.session_state['india_view'] = 'state_trend'

    # View rendering
    if st.session_state['india_view'] == 'state_trend':
        display_state_trend_analysis()
    elif st.session_state['india_view'] == 'bar':
        display_india_bar_analysis()


def display_state_trend_analysis():
    """
    Display state-wise trend analysis for India using preprocessed data
    """
    st.subheader("📈 State-wise Maize Yield Trends")
    
    data = st.session_state['india_preprocessed_data_1']
    
    # Check if state data exists
    if not data['has_state_data']:
        st.warning("State information not found in dataset. Showing national trends.")
        
        # Plot national trend using preprocessed data
        plt.figure(figsize=(20, 8))
        plt.plot(data['national_yearly']['year'], data['national_yearly']['yield'], 
                'r-', linewidth=3, marker='o', markersize=8, label='National Average')
        
        plt.title('National Maize Yield Trend in India', fontsize=16)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('Yield (Tons/Ha)', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        st.pyplot(plt)
    else:
        # State selection
        selected_states = st.multiselect(
            "Select States to Compare",
            data['available_states'],
            default=data['available_states'][:3] if len(data['available_states']) > 3 else data['available_states']
        )
        
        if not selected_states:
            st.warning("Please select at least one state")
        else:
            # Filter preprocessed data for selected states
            state_trends = data['state_year_data'][data['state_year_data']['State'].isin(selected_states)]
            
            # Create the plot using Plotly for better interactivity
            fig = px.line(
                state_trends,
                x='year',
                y='yield',
                color='State',
                title='State-wise Maize Yield Trends in India',
                labels={'year': 'Year', 'yield': 'Yield (Tons/Ha)'},
                markers=True
            )
            
            # Enhance plot aesthetics
            fig.update_layout(
                xaxis_title='Year',
                yaxis_title='Yield (Tons/Ha)',
                legend_title='State',
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display statistics
            st.subheader("📊 State-wise Statistics")
            
            # Calculate latest year stats
            latest_year = state_trends['year'].max()
            latest_data = state_trends[state_trends['year'] == latest_year].sort_values('yield', ascending=False)
            
            cols = st.columns(3)
            with cols[0]:
                if not latest_data.empty:
                    top_state = latest_data.iloc[0]
                    st.metric(
                        label=f"Highest Yield ({int(latest_year)})",
                        value=top_state['State'],
                        delta=f"{top_state['yield']:.2f} Tons/Ha"
                    )
            
            with cols[1]:
                if not latest_data.empty:
                    avg_yield = latest_data['yield'].mean()
                    st.metric(
                        label=f"Average Yield ({int(latest_year)})",
                        value=f"{avg_yield:.2f} Tons/Ha"
                    )
            
            with cols[2]:
                if len(latest_data) > 1:
                    lowest_state = latest_data.iloc[-1]
                    st.metric(
                        label=f"Lowest Yield ({int(latest_year)})",
                        value=lowest_state['State'],
                        delta=f"{lowest_state['yield']:.2f} Tons/Ha"
                    )


def display_india_bar_analysis():
    """
    Display bar graph analysis for India (state-wise) using preprocessed data
    """
    st.subheader("📊 State-wise Yield Bar Graph Analysis")
    
    data = st.session_state['india_preprocessed_data_1']

    # Control panel
    year_range = st.slider(
        "Select Year Range",
        min_value=data['min_year'],
        max_value=data['max_year'],
        value=(data['min_year'], data['max_year'])
    )

    # Filter data for selected year range
    if data['has_state_data']:
        # Filter preprocessed data for year range
        yearly_data = data['filtered_data'][
            data['filtered_data']['year'].between(year_range[0], year_range[1])
        ]
        
        if not yearly_data.empty:
            # Group by state
            state_yield = yearly_data.groupby('State')['yield'].mean().reset_index()
            state_yield = state_yield.sort_values('yield', ascending=False)

            # Create bar plot with Plotly
            fig = px.bar(
                state_yield,
                x='State',
                y='yield',
                title=f'State-wise Yield Distribution in India ({year_range[0]} – {year_range[1]})',
                labels={'State': 'State', 'yield': 'Yield (Tons/Ha)'},
                color='yield',
                text_auto='.2f'
            )

            fig.update_layout(
                xaxis_tickangle=45,
                template='plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No data available for year range ({year_range[0]} – {year_range[1]})")
    else:
        st.warning("State information not found in dataset.")

# Add a reset button function to clear cached data if needed
def add_reset_india_cache():
    if st.sidebar.button("Reset India Data Cache"):
        if 'india_preprocessed_data_1' in st.session_state:
            del st.session_state['india_preprocessed_data_1']
        if 'india_view' in st.session_state:
            del st.session_state['india_view']
        st.experimental_rerun()