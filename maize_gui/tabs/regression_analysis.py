import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def display_regression_analysis(india_data):
    st.subheader("📊 Interactive Climate and Yield Analysis")
    
    # Check if data is already preprocessed and stored in session state
    if 'regression_preprocessed_data' not in st.session_state:
        with st.spinner("Processing data for analysis... Please wait"):
            try:
                # Determine column names for latitude and longitude
                lon_col = 'longitude' if 'longitude' in india_data.columns else 'lon'
                lat_col = 'latitude' if 'latitude' in india_data.columns else 'lat'

                required_columns = ['year', lon_col, lat_col, 'tas', 'pr', 'tasmax', 'tasmin',
                                    'texture_class', 'rds', 'nitrogen', 'co2', 'Day', 'yield']
                missing_columns = [col for col in required_columns if col not in india_data.columns]

                if missing_columns:
                    st.error(f"Missing columns in data: {', '.join(missing_columns)}")
                    st.info("Please make sure the data contains all required columns for analysis.")
                    return

                # Process data once
                processed_data = prepare_data_for_analysis(india_data, lon_col, lat_col)
                
                if processed_data is None or processed_data.empty:
                    st.error("No data available for analysis after processing.")
                    return
                
                # Create variable lists and labels once
                variables = ['pr', 'tas', 'tasmin', 'tasmax', 'rds', 'co2', 'nitrogen']
                variables = [var for var in variables if var in processed_data.columns]
                
                labels = {
                    'pr': 'Precipitation (kg/m²/s)',
                    'tas': 'Mean Temperature (°C)',
                    'tasmin': 'Minimum Temperature (°C)',
                    'tasmax': 'Maximum Temperature (°C)',
                    'rds': 'Shortwave Radiation (W/m²)',
                    'co2': 'CO2 (ppm)',
                    'nitrogen': 'Nitrogen (tons/ha)'
                }
                
                # Store preprocessed data and metadata in session state
                st.session_state['regression_preprocessed_data'] = {
                    'processed_data': processed_data,
                    'variables': variables,
                    'labels': labels,
                    'min_year': int(processed_data['year'].min()),
                    'max_year': int(processed_data['year'].max())
                }
                
            except Exception as e:
                st.error(f"Error in data preprocessing: {str(e)}")
                return
    
    # Retrieve preprocessed data from session state
    data = st.session_state['regression_preprocessed_data']
    
    # View selector buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Scatter Plot Analysis"):
            st.session_state['regression_view'] = 'scatter'
    with col2:
        if st.button("Time Series Analysis"):
            st.session_state['regression_view'] = 'time_series'

    # Set default view if not already set
    if 'regression_view' not in st.session_state:
        st.session_state['regression_view'] = 'scatter'

    # Year range filter
    try:
        year_range = st.slider(
            "Select Year Range for Analysis",
            min_value=data['min_year'],
            max_value=data['max_year'],
            value=(data['min_year'], data['max_year'])
        )
        
        # Filter preprocessed data based on year range
        filtered_data = data['processed_data'][
            data['processed_data']['year'].between(year_range[0], year_range[1])
        ]
    except Exception as e:
        st.error(f"Error setting year range: {str(e)}")
        st.info("Using full dataset instead.")
        filtered_data = data['processed_data']

    # Display the selected view using filtered data
    if st.session_state['regression_view'] == 'scatter':
        display_scatter_analysis(filtered_data, data['variables'], data['labels'])
    elif st.session_state['regression_view'] == 'time_series':
        display_time_series_analysis(filtered_data, data['variables'], data['labels'])


def prepare_data_for_analysis(country, lon_col, lat_col):
    """Process data once for analysis"""
    try:
        # Average features across days for each year/location
        average_features = country.groupby(['year', lon_col, lat_col])[
            ['tas', 'pr', 'tasmax', 'tasmin', 'texture_class', 'rds', 'nitrogen', 'co2']
        ].mean().reset_index()

        # Get target yield data (from day 239)
        target_yield = country[country['Day'] == 239][['year', lon_col, lat_col, 'yield']]

        # Merge features with target
        merged_data = pd.merge(
            average_features,
            target_yield,
            on=['year', lon_col, lat_col],
            how='inner'
        )

        # Select only numeric columns
        numeric_df = merged_data.select_dtypes(include=[np.number])

        # Ensure year column is included
        if 'year' not in numeric_df.columns and 'year' in merged_data.columns:
            numeric_df['year'] = merged_data['year']

        # Group by year to get yearly averages
        grouped_data = numeric_df.groupby('year', as_index=False).mean()

        return grouped_data

    except Exception as e:
        return None


def display_scatter_analysis(filtered_data, variables, labels):
    """Display scatter plot analysis with preprocessed data"""
    st.subheader("Relationship between Climate Factors and Yield")
    
    if not variables:
        st.error("No analysis variables found in the data.")
        return
    
    titles = labels  # Use labels as titles
    
    # Variable selection
    default_vars = variables[:min(3, len(variables))]
    selected_vars = st.multiselect(
        "Select variables to display",
        options=variables,
        default=default_vars,
        format_func=lambda x: titles.get(x, x)
    )

    if not selected_vars:
        st.info("Please select at least one variable to display")
        return

    # Calculate subplot layout
    n_vars = len(selected_vars)
    n_cols = min(3, n_vars)
    n_rows = (n_vars + n_cols - 1) // n_cols

    # Create subplots
    fig = make_subplots(
        rows=n_rows, 
        cols=n_cols,
        subplot_titles=[titles.get(var, var) for var in selected_vars]
    )

    # Add traces for each variable
    for i, var in enumerate(selected_vars):
        row = i // n_cols + 1
        col = i % n_cols + 1
        x = filtered_data[var]
        y = filtered_data['yield']

        # Add scatter plot
        scatter = go.Scatter(
            x=x,
            y=y,
            mode='markers',
            name=titles.get(var, var),
            marker=dict(
                size=8,
                color=filtered_data['year'],
                colorscale='Viridis',
                colorbar=dict(title="Year") if i == 0 else None,
                showscale=i == 0
            ),
            hovertemplate=
            f'Year: %{{customdata}}<br>' +
            f'{labels.get(var, var)}: %{{x}}<br>' +
            'Yield: %{y} tons/ha<extra></extra>',
            customdata=filtered_data['year']
        )
        fig.add_trace(scatter, row=row, col=col)

        # Add trendline if enough valid data points
        if x.notna().sum() > 1 and y.notna().sum() > 1:
            try:
                valid_mask = x.notna() & y.notna()
                if valid_mask.sum() >= 2:
                    z = np.polyfit(x[valid_mask], y[valid_mask], 1)
                    p = np.poly1d(z)
                    x_range = np.linspace(x.min(), x.max(), 100)

                    trend = go.Scatter(
                        x=x_range,
                        y=p(x_range),
                        mode='lines',
                        name=f'Trend ({titles.get(var, var)})',
                        line=dict(color='rgba(255, 0, 0, 0.8)'),
                        showlegend=False
                    )
                    fig.add_trace(trend, row=row, col=col)
            except Exception as e:
                pass  # Skip trendline if calculation fails

        # Update axes titles
        fig.update_xaxes(title_text=labels.get(var, var), row=row, col=col)
        if col == 1:
            fig.update_yaxes(title_text='Yield (tons/ha)', row=row, col=col)

    # Update layout
    fig.update_layout(
        height=300 * n_rows,
        width=900,
        title_text="Climate Factors vs. Maize Yield in India",
        showlegend=False,
        hovermode="closest"
    )

    st.plotly_chart(fig, use_container_width=True)


def display_time_series_analysis(filtered_data, variables, labels):
    """Display time series analysis with preprocessed data"""
    st.subheader("Yield and Selected Factors Over Time")
    
    if not variables:
        st.error("No time-series variables found in the data.")
        return

    # Variable selection for time series
    default_time_vars = variables
    time_vars = st.multiselect(
        "Select factors to compare with yield over time",
        options=variables,
        default=default_time_vars,
        format_func=lambda x: x.upper()
    )

    if not time_vars:
        st.info("Please select at least one variable to display")
        return

    # Create the base time series figure with yield
    fig = px.line(
        filtered_data,
        x='year',
        y='yield',
        title='Yield and Selected Factors Over Time',
        labels={'year': 'Year', 'yield': 'Yield (tons/ha)'}
    )

    # Create a copy of filtered data for normalization
    # This avoids modifying the original data which might be used elsewhere
    norm_data = filtered_data.copy()
    
    # Add normalized traces for each selected variable
    for var in time_vars:
        try:
            # Normalize values to fit on same scale as yield
            if norm_data[var].max() != norm_data[var].min():
                norm_data[f'{var}_norm'] = (norm_data[var] - norm_data[var].min()) / (
                        norm_data[var].max() - norm_data[var].min()) * 0.8 + 0.1
            else:
                norm_data[f'{var}_norm'] = 0.5

            # Add variable as second y-axis
            fig.add_scatter(
                x=norm_data['year'],
                y=norm_data[f'{var}_norm'],
                name=var.upper(),
                line=dict(dash='dash'),
                yaxis='y2',
                hovertemplate=
                f'Year: %{{x}}<br>' +
                f'{var.upper()}: %{{customdata}}<br>' +
                '<extra></extra>',
                customdata=norm_data[var]
            )
        except Exception as e:
            st.warning(f"Could not plot {var}: {str(e)}")

    # Update layout with second y-axis
    fig.update_layout(
        yaxis2=dict(
            title="Normalized Values",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(orientation="h", y=1.1),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Correlation analysis
    st.subheader("Correlation Analysis")
    try:
        # Only calculate correlation for selected variables
        correlation_vars = ['yield'] + time_vars
        corr_matrix = filtered_data[correlation_vars].corr()
        
        # Create heatmap
        fig_heatmap = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Correlation Matrix"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    except Exception as e:
        st.error(f"Could not create correlation heatmap: {str(e)}")

# Add a reset button function to clear cached data if needed
def reset_regression_cache():
    if st.sidebar.button("Reset Regression Analysis Cache"):
        if 'regression_preprocessed_data' in st.session_state:
            del st.session_state['regression_preprocessed_data']
        if 'regression_view' in st.session_state:
            del st.session_state['regression_view']
        st.experimental_rerun()