import streamlit as st
import plotly.express as px

def display_predicted_country_analysis(df_all_countries):
    """
    Display the country-wise analysis page with trendline and bar graph options
    
    Args:
        df_all_countries: DataFrame containing all country data
    """
    st.subheader("Country-wise Analysis")
    
    # Sub-navigation for Country Analysis
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Trendline Analysis"):
            st.session_state['country_view'] = 'trendline'
    with col2:
        if st.button("Bar Graph Analysis"):
            st.session_state['country_view'] = 'bar'
    
    # Default view
    if 'country_view' not in st.session_state:
        st.session_state['country_view'] = 'trendline'
    
    # Show the selected view
    if st.session_state['country_view'] == 'trendline':
        display_trendline_analysis(df_all_countries)
    elif st.session_state['country_view'] == 'bar':
        display_bar_analysis(df_all_countries)

def display_trendline_analysis(df_all_countries):
    """
    Display trendline analysis view with interactive charts
    
    Args:
        df_all_countries: DataFrame containing all country data
    """
    st.subheader("📈 Trendline Analysis")
    
    # Control panel
    st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
    selected_countries = st.multiselect(
        "Select Countries to Compare",
        sorted(df_all_countries['Country'].unique()),
        default=sorted(df_all_countries['Country'].unique())
    )
    
    year_range = st.slider(
        "Select Year Range",
        min_value=int(df_all_countries['year'].min()),
        max_value=int(df_all_countries['year'].max()),
        value=(int(df_all_countries['year'].min()), int(df_all_countries['year'].max()))
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Filter data based on user selections
    df_filtered = df_all_countries[
        (df_all_countries['Country'].isin(selected_countries)) &
        (df_all_countries['year'].between(year_range[0], year_range[1]))
    ]
    
    
    df_filtered = df_filtered[df_filtered['Day'] == 239]
    
    # Group by year and country to get average yield
    df_grouped = df_filtered.groupby(['year', 'Country'])['yield'].mean().reset_index()
    
    # Interactive Line Chart
    fig = px.line(
        df_grouped,
        x='year',
        y='yield',
        color='Country',
        title='Yearly Maize Yield Trends',
        labels={'year': 'Year', 'yield': 'Yield (Tons/Ha)'},
        template='plotly_white',
        height=600
    )
    
    # Customize chart layout
    fig.update_layout(
        hovermode='x unified',
        legend_title_text='Country',
        xaxis_title='Year',
        yaxis_title='Yield (Tons/Ha)',
        font=dict(size=12),
        hoverlabel=dict(bgcolor='#323232', font_size=12, font_color='white')
    )
    
    # Add range slider and selector
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(count=10, label="10y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    # Display interactive chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights Section
    if not df_grouped.empty:
        st.subheader("🔍 Key Insights")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Highest Overall Yield",
                value=f"{df_grouped['yield'].max():.2f} Tons/Ha",
                delta=f"Country: {df_grouped.loc[df_grouped['yield'].idxmax(), 'Country']}"
            )
        
        with col2:
            st.metric(
                label="Lowest Overall Yield",
                value=f"{df_grouped['yield'].min():.2f} Tons/Ha",
                delta=f"Country: {df_grouped.loc[df_grouped['yield'].idxmin(), 'Country']}"
            )
        
        with col3:
            st.metric(
                label="Average Yield",
                value=f"{df_grouped['yield'].mean():.2f} Tons/Ha"
            )

def display_bar_analysis(df_all_countries):
    """
    Display bar graph analysis view

    Args:
        df_all_countries: DataFrame containing all country data
    """
    st.subheader("📊 Bar Graph Analysis")

    # Control panel for the bar chart
    st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
    selected_countries_bar = st.multiselect(
        "Select Countries",
        sorted(df_all_countries['Country'].unique()),
        default=sorted(df_all_countries['Country'].unique())
    )

    year_range = st.slider(
        "Select Year Range",
        min_value=int(df_all_countries['year'].min()),
        max_value=int(df_all_countries['year'].max()),
        value=(
            int(df_all_countries['year'].min()),
            int(df_all_countries['year'].max())
        )
    )


    
    sort_order = st.radio(
        "Sort Order",
        ["Ascending", "Descending"],
        horizontal=True,
        index=1
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Filter data based on selections
    df_bar = df_all_countries[
        (df_all_countries['Country'].isin(selected_countries_bar)) &
        (df_all_countries['year'].between(year_range[0], year_range[1]))
    ]
    
    df_bar = df_bar[df_bar['Day'] == 239]
    
    # Group by country to get average yield
    df_grouped = df_bar.groupby('Country')['yield'].mean().reset_index()

    # Create bar chart with Plotly
    if not df_grouped.empty:
        df_grouped = df_grouped.sort_values(by='yield', ascending=(sort_order == "Ascending"))

        fig_bar = px.bar(
            df_grouped,
            x='yield',
            y='Country',
            orientation='h',
            color='Country',
            title=f'Maize Yield by Country ({year_range[0]} – {year_range[1]})',
            labels={'yield': 'Yield (Tons/Ha)'},
            template='plotly_white',
            height=600
        )

        # Add value labels inside bars
        fig_bar.update_traces(texttemplate='%{x:.2f}', textposition='inside')

        # Customize layout
        fig_bar.update_layout(
            showlegend=False,
            xaxis_title='Yield (Tons/Ha)',
            yaxis_title='Country',
            hoverlabel=dict(bgcolor='#323232', font_size=12, font_color='white')
        )

        st.plotly_chart(fig_bar, use_container_width=True)

        # Statistics
        if len(selected_countries_bar) > 1:
            st.subheader("📈 Statistics")
            col1, col2 = st.columns(2)

            with col1:
                highest_country = df_grouped.loc[df_grouped['yield'].idxmax(), 'Country']
                highest_yield = df_grouped['yield'].max()
                st.info(f"**Highest Yield**: {highest_country} ({highest_yield:.2f} Tons/Ha)")

            with col2:
                avg_yield = df_grouped['yield'].mean()
                st.info(f"**Average Yield**: {avg_yield:.2f} Tons/Ha")
    else:
        st.warning("No data available for the selected filters.")